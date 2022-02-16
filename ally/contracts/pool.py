import os

from pyteal import *

total_supply = 0xFFFFFFFFFFFFFFFF

gov_key = Bytes("gov")
pool_token_key = Bytes("p")
mint_price_key = Bytes("mp")
redeem_price_key = Bytes("rp")
commited_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")

action_update = Bytes("set_governor")
action_boot = Bytes("bootstrap")
action_mint_price = Bytes("set_mint_price")
action_redeem_price = Bytes("set_redeem_price")
action_toggle = Bytes("toggle_redeem")
action_join = Bytes("join")
action_vote = Bytes("vote")
action_mint = Bytes("mint")
action_redeem = Bytes("redeem")

# Takes unix timestamp for locked windows
def approval(lock_start: int = 0, lock_stop: int = 0):
    assert lock_start < lock_stop

    # Alias commonly used things
    me = Global.current_application_address()
    pool_token = App.globalGet(pool_token_key)
    pool_balance = AssetHolding.balance(me, pool_token)

    governor = App.globalGet(gov_key)   

    # Checks for if we're in the window for this action
    before_lock_start = Global.latest_timestamp() < Int(lock_start)
    after_lock_stop = Global.latest_timestamp() > Int(lock_stop)

    @Subroutine(TealType.uint64)
    def mint_tokens(algos_in: TealType.uint64):
        # Mint in 1:1 with algos passed in
        mint_amount = WideRatio(
            [App.globalGet(mint_price_key), algos_in],
            [Int(1_000_000_000)]
        )
        return Seq(
            Return(mint_amount)
        )

    @Subroutine(TealType.uint64)
    def algos_to_redeem(amt: TealType.uint64):
        algos = WideRatio(
            [App.globalGet(redeem_price_key), amt],
            [Int(1_000_000_000)]
        )
        return Seq(
            Return(algos)
        )

    @Subroutine(TealType.none)
    def axfer(receiver: TealType.bytes, aid: TealType.uint64, amt: TealType.uint64):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.AssetTransfer,
                    TxnField.xfer_asset: aid,
                    TxnField.asset_amount: amt,
                    TxnField.asset_receiver: receiver,
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    @Subroutine(TealType.none)
    def pay(receiver: TealType.bytes, amt: TealType.uint64):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: amt,
                    TxnField.receiver: receiver
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    def bootstrap():
        pool_token_check = App.globalGetEx(Int(0), pool_token_key)
        governor = App.globalGet(gov_key)
        return Seq(
            pool_token_check,
            # Make sure we've not already set this
            Assert(Not(pool_token_check.hasValue())),
            Assert(Txn.sender() == governor),
            # Create the pool token
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Bytes("wALGO"),
                TxnField.config_asset_unit_name: Bytes("wALGO"),
                TxnField.config_asset_url: Bytes("https://maxos.studio"),
                TxnField.config_asset_total: Int(total_supply),
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_manager: Global.zero_address(),
                TxnField.config_asset_reserve: Global.zero_address(),
                TxnField.config_asset_clawback: Global.zero_address(),
                TxnField.config_asset_freeze: Global.zero_address(),
            }),
            InnerTxnBuilder.Submit(),
            # Write it to global state
            App.globalPut(pool_token_key,
                          InnerTxn.created_asset_id()),
            Approve(),
        )

    def set_governor():
        new_gov = Txn.accounts[1]
        governor = App.globalGet(gov_key)
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(gov_key, new_gov),
            Approve()
        )

    def set_mint_price():
        new_mint_price = Txn.application_args[1]
        governor = App.globalGet(gov_key)
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(mint_price_key, Btoi(new_mint_price)),
            Approve()
        )


    def set_redeem_price():
        new_redeem_price = Txn.application_args[0]
        governor = App.globalGet(gov_key)
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(redeem_price_key, Btoi(new_redeem_price)),
            Approve()
        )

    def toggle_redeem():
        governor = App.globalGet(gov_key)
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(allow_redeem_key, Not(
                App.globalGet(allow_redeem_key))),
            Approve()
        )

    def join():
        governor = App.globalGet(gov_key)
        return Seq(
            Assert(
                And(
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.sender() == governor,
                )
            ),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.accounts[1],  # address of goverance
                TxnField.amount: Int(0),
                TxnField.note: Txn.application_args[
                    1
                ],  # expecting a valid note as the 2nd element in app args array
            }),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    def vote():
        algos_to_commit = Btoi(Txn.application_args[1])
        return Seq(
            # TODO:
            Approve(),
        )

    def mint():
        pool_token = App.globalGet(pool_token_key)
        pool_bal = AssetHolding.balance(Global.current_application_address(), pool_token)
        return Seq(
            # Init MaybeValues
            pool_bal,
            Assert(
                And(
                    Global.group_size() == Int(2),  # App call, Payment to mint
                    Gtxn[0].type_enum() == TxnType.ApplicationCall,
                    Gtxn[0].assets[0] == pool_token,
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == Global.current_application_address(),
                    Gtxn[1].amount() > Int(1_000),
                    Gtxn[1].sender() == Gtxn[0].sender(),
                )
            ),
            axfer(
                Gtxn[0].sender(),
                pool_token,
                mint_tokens(Gtxn[1].amount() - Int(1_000))
            ),
            Approve(),
        )

    def redeem():
        pool_token = App.globalGet(pool_token_key)
        pool_bal = AssetHolding.balance(
            Global.current_application_address(), pool_token)
        return Seq(
            Assert(App.globalGet(allow_redeem_key)),
            Assert(
                And(
                    Global.group_size() == Int(2),
                    Gtxn[0].type_enum() == TxnType.ApplicationCall,
                    Gtxn[0].assets[0] == pool_token,
                    Gtxn[1].type_enum() == TxnType.AssetTransfer,
                    Gtxn[1].asset_receiver() == Global.current_application_address(),
                    Gtxn[1].xfer_asset() == pool_token,
                    Gtxn[0].sender() == Gtxn[1].sender(),
                )
            ),
            pool_bal,
            pay(Gtxn[1].sender(), algos_to_redeem(Gtxn[1].asset_amount())),
            Approve(),
        )

    handle_creation = Seq(
        App.globalPut(mint_price_key, Int(1_000_000_000)),
        App.globalPut(redeem_price_key, Int(1_000_000_000)),
        App.globalPut(allow_redeem_key, Int(1)),
        App.globalPut(commited_algos_key, Int(0)),
        App.globalPut(gov_key, Txn.sender()),
        Approve()
    )

    router = Cond(
        [Txn.application_args[0] == action_boot, bootstrap()],
        [Txn.application_args[0] == action_update, set_governor()],
        [Txn.application_args[0] == action_mint_price, set_mint_price()],
        [Txn.application_args[0] == action_redeem_price, set_redeem_price()],
        [Txn.application_args[0] == action_toggle, toggle_redeem()],
        [Txn.application_args[0] == action_join, join()],
        [Txn.application_args[0] == action_vote, vote()],
        [Txn.application_args[0] == action_mint, mint()],
        [Txn.application_args[0] == action_redeem, redeem()],
    )

    return Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Txn.sender() == governor)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Txn.sender() == governor)],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Reject()],
        [Txn.on_completion() == OnComplete.NoOp, router],
    )


def clear():
    return Approve()

def get_approval_src(**kwargs):
    return compileTeal(approval(**kwargs), mode=Mode.Application, version=5)


def get_clear_src(**kwargs):
    return compileTeal(clear(**kwargs), mode=Mode.Application, version=5)

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(get_approval_src(lock_start=1, lock_stop=10))

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(get_clear_src())