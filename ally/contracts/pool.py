import os

from pyteal import *

TOTAL_SUPPLY = 0xFFFFFFFFFFFFFFFF
ONE_ALGO_IN_MICRO = 1_000_000_000 # TODO test with 1M

governor_key = Bytes("gv")
pool_token_key = Bytes("pt")
mint_price_key = Bytes("mp")
redeem_price_key = Bytes("rp")
commited_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")

action_governor = Bytes("set_governor")
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

    governor = App.globalGet(governor_key)

    # Checks for if we're in the window for this action
    before_lock_start = Global.latest_timestamp() < Int(lock_start)
    after_lock_stop = Global.latest_timestamp() > Int(lock_stop)

    # Amount of walgos to mint based on the paid algos
    @Subroutine(TealType.uint64)
    def walgos_to_mint(microalgos: TealType.uint64):
        amount = WideRatio(
            [App.globalGet(mint_price_key), microalgos],
            [Int(ONE_ALGO_IN_MICRO)]
        )
        return Seq(
            Return(amount)
        )

    # ALGOs to pay based on the burned wALGOs amount
    @Subroutine(TealType.uint64)
    def algos_to_redeem(amount: TealType.uint64):
        algos = WideRatio(
            [App.globalGet(redeem_price_key), amount],
            [Int(ONE_ALGO_IN_MICRO)]
        )
        return Seq(
            Return(algos)
        )

    # Function to make an asset transfer
    @Subroutine(TealType.none)
    def axfer(receiver: TealType.bytes, asset_id: TealType.uint64, amount: TealType.uint64):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.AssetTransfer,
                    TxnField.xfer_asset: asset_id,
                    TxnField.asset_amount: amount,
                    TxnField.asset_receiver: receiver,
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    # Function to make a payment transfer
    @Subroutine(TealType.none)
    def pay(receiver: TealType.bytes, amount: TealType.uint64):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: amount,
                    TxnField.receiver: receiver
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    # Function to boot the app after creation - sets up the walgo asset
    def bootstrap():
        contract_address = Global.current_application_address()
        pool_token_check = App.globalGetEx(Int(0), pool_token_key)
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
                TxnField.config_asset_total: Int(TOTAL_SUPPLY),
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_manager: contract_address,
                TxnField.config_asset_reserve: contract_address,
            }),
            InnerTxnBuilder.Submit(),
            # Write it to global state
            App.globalPut(pool_token_key, InnerTxn.created_asset_id()),
            Approve(),
        )

    # Function to set a new governor - admin action
    def set_governor():
        new_governor = Txn.accounts[1]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(governor_key, new_governor),
            Approve()
        )

    # Function to set a new mint price - admin action
    def set_mint_price():
        new_mint_price = Txn.application_args[1]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(mint_price_key, Btoi(new_mint_price)),
            Approve()
        )

    # Function to set a new redeem price - admin action
    def set_redeem_price():
        new_redeem_price = Txn.application_args[1]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(redeem_price_key, Btoi(new_redeem_price)),
            Approve()
        )

    # Function to enable/disable redemption - admin action
    def toggle_redeem():
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(allow_redeem_key, Not(App.globalGet(allow_redeem_key))),
            Approve()
        )

    def join():
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
                ], # expecting a valid note as the 2nd element in app args array
            }),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    def vote():
        app_call = Gtxn[0]
        well_formed_vote = And(
            Global.group_size() == Int(1),
            app_call.type_enum() == TxnType.ApplicationCall,
            app_call.sender() == governor,
        )
        return Seq(
            # TODO: uncomment when done testing on dev
            # Assert(!before_lock_start),
            # Assert(!after_lock_stop),
            Assert(well_formed_vote),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(0),
                    TxnField.note: Txn.application_args[
                        1
                    ],  # expecting a valid note as the 2nd element in app args array
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    # Function to mint new walgo tokens - user action
    def mint():
        contract_address = Global.current_application_address()
        pool_token = App.globalGet(pool_token_key)
        pool_balance = AssetHolding.balance(contract_address, pool_token)
        app_call = Gtxn[0]
        payment = Gtxn[1]
        return Seq(
            pool_balance,
            Assert(
                And(
                    # before_lock_start, # TODO: uncomment when done testing on dev
                    Global.group_size() == Int(2),  # App call, Payment to mint
                    app_call.type_enum() == TxnType.ApplicationCall,
                    app_call.assets[0] == pool_token,
                    payment.type_enum() == TxnType.Payment,
                    payment.sender() == app_call.sender(),
                    payment.receiver() == contract_address,
                    payment.amount() > Int(1_000), # TODO use payment.fee()
                )
            ),
            axfer(
                payment.sender(),
                pool_token,
                walgos_to_mint(payment.amount() - Int(1_000)) # TODO use payment.fee()
            ),
            Approve(),
        )

    # Function to redeem users' walgo tokens - user action
    def redeem():
        contract_address = Global.current_application_address()
        pool_token = App.globalGet(pool_token_key)
        pool_balance = AssetHolding.balance(contract_address, pool_token)
        app_call = Gtxn[0]
        asset_xfer = Gtxn[1]
        return Seq(
            Assert(App.globalGet(allow_redeem_key)),
            Assert(
                And(
                    # after_lock_stop, # TODO: uncomment when done testing on dev
                    Global.group_size() == Int(2),
                    app_call.type_enum() == TxnType.ApplicationCall,
                    app_call.assets[0] == pool_token,
                    asset_xfer.type_enum() == TxnType.AssetTransfer,
                    asset_xfer.sender() == app_call.sender(),
                    asset_xfer.asset_receiver() == contract_address,
                    asset_xfer.xfer_asset() == pool_token,
                )
            ),
            pool_balance,
            pay(
                asset_xfer.sender(),
                algos_to_redeem(asset_xfer.asset_amount())
            ),
            Approve(),
        )

    # Initialize the Global State on creation
    handle_creation = Seq(
        App.globalPut(mint_price_key, Int(ONE_ALGO_IN_MICRO)),
        App.globalPut(redeem_price_key, Int(ONE_ALGO_IN_MICRO)),
        App.globalPut(allow_redeem_key, Int(1)),
        App.globalPut(commited_algos_key, Int(0)),
        App.globalPut(governor_key, Txn.sender()),
        Approve()
    )

    # Routes the NoOp to the corresponding action based on the first app param
    router = Cond(
        [Txn.application_args[0] == action_boot, bootstrap()],
        [Txn.application_args[0] == action_governor, set_governor()],
        [Txn.application_args[0] == action_mint_price, set_mint_price()],
        [Txn.application_args[0] == action_redeem_price, set_redeem_price()],
        [Txn.application_args[0] == action_toggle, toggle_redeem()],
        [Txn.application_args[0] == action_join, join()],
        [Txn.application_args[0] == action_vote, vote()],
        [Txn.application_args[0] == action_mint, mint()],
        [Txn.application_args[0] == action_redeem, redeem()],
    )

    # Routes the OnComplete actions to the corresponding action
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

# Compiling functions
def get_approval_src(**kwargs):
    return compileTeal(approval(**kwargs), mode=Mode.Application, version=5)

def get_clear_src(**kwargs):
    return compileTeal(clear(**kwargs), mode=Mode.Application, version=5)

# When executing this file, compile this PyTeal into TEAL
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(get_approval_src(lock_start=1, lock_stop=10))

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(get_clear_src())
