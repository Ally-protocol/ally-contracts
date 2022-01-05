import os

from pyteal import *


gov_key = Bytes("gov")
pool_token_key = Bytes("p")
mint_price_key = Bytes("mp")
redeem_price_key = Bytes("rp")
commited_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")

total_supply = 0xFFFFFFFFFFFFFFFF


# Takes unix timestamp for locked windows
def approval():
    pool_token = App.globalGet(pool_token_key)
    governor = App.globalGet(gov_key)

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
    def axfer(reciever: TealType.bytes, aid: TealType.uint64, amt: TealType.uint64):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.AssetTransfer,
                    TxnField.xfer_asset: aid,
                    TxnField.asset_amount: amt,
                    TxnField.asset_receiver: reciever,
                    TxnField.fee: Int(0),
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
                    TxnField.receiver: receiver,
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    on_create = Seq(
        App.globalPut(mint_price_key, Int(1_000_000_000)),
        App.globalPut(redeem_price_key, Int(1_000_000_000)),
        App.globalPut(allow_redeem_key, Int(1)),
        App.globalPut(commited_algos_key, Int(0)),
        Approve()
    )

    pool_token_check = App.globalGetEx(Int(0), pool_token_key)
    on_bootstrap = Seq(
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
            TxnField.fee: Int(0),
        }),
        InnerTxnBuilder.Submit(),
        # Write it to global state
        App.globalPut(pool_token_key, InnerTxn.created_asset_id()),
        Approve(),
    )

    new_gov = Txn.accounts[1]
    on_set_governor = Seq(
        Assert(Txn.sender() == governor),
        App.globalPut(gov_key, new_gov),
        Approve()
    )

    new_mint_price = Txn.application_args[0]
    on_set_mint_price = Seq(
        Assert(Txn.sender() == governor),
        App.globalPut(mint_price_key, Btoi(new_mint_price)),
        Approve()
    )
    
    new_redeem_price = Txn.application_args[0]
    on_set_redeem_price = Seq(
        Assert(Txn.sender() == governor),
        App.globalPut(redeem_price_key, Btoi(new_redeem_price)),
        Approve()
    )
    
    on_toggle_redeem = Seq(
        Assert(Txn.sender() == governor),
        App.globalPut(allow_redeem_key, Not(App.globalGet(allow_redeem_key))),
        Approve()
    )

    on_join = Seq(
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
            TxnField.fee: Int(0),
        }),
        InnerTxnBuilder.Submit(),
        Approve(),
    )
    
    algos_to_commit = Btoi(Txn.application_args[1])
    on_vote = Seq(
        # TODO: 
        Approve(),
    )

    pool_bal = AssetHolding.balance(
        Global.current_application_address(), pool_token)
    on_mint = Seq(
        # Init MaybeValues
        pool_bal,
        Assert(
            And(
                Global.group_size() == Int(2),  # App call, Payment to mint
                Gtxn[0].type_enum() == TxnType.ApplicationCall,
                Gtxn[0].assets[0] == pool_token,
                Gtxn[1].type_enum() == TxnType.Payment,
                Gtxn[1].receiver() == Global.current_application_address(),
                Gtxn[1].amount() > Int(0),
                Gtxn[1].sender() == Gtxn[0].sender(),
            )
        ),
        axfer(Gtxn[0].sender(), pool_token, mint_tokens(Gtxn[1].amount())),
        Approve(),
    )

    pool_bal = AssetHolding.balance(
        Global.current_application_address(), pool_token)
    on_redeem = Seq(
        Assert(App.globalGet(allow_redeem_key)),
        pool_bal,
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
        pay(Gtxn[1].sender(), algos_to_redeem(Gtxn[1].asset_amount())),
        Approve(),
    )

    on_call_method = Txn.application_args[0]
    on_call = Cond(
        # Admin
        [on_call_method == Bytes("bootstrap"), on_bootstrap],
        [on_call_method == Bytes("set_governor"), on_set_governor],
        [on_call_method == Bytes("set_mint_price"), on_set_mint_price],
        [on_call_method == Bytes("set_redeem_price"), on_set_redeem_price],
        [on_call_method == Bytes("toggle_redeem"), on_toggle_redeem],
        [on_call_method == Bytes("join"), on_join],
        [on_call_method == Bytes("vote"), on_vote],
        # Users
        [on_call_method == Bytes("mint"), on_mint],
        [on_call_method == Bytes("redeem"), on_redeem],
    )

    return Cond(
        [Txn.application_id() == Int(0), on_create],
        [
            Txn.on_completion() == OnComplete.DeleteApplication,
            Return(Txn.sender() == governor)
        ],
        [
            Txn.on_completion() == OnComplete.UpdateApplication,
            Return(Txn.sender() == governor)
        ],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Reject()],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
    )


def clear():
    return Return(Int(1))


def get_approval_src():
    return compileTeal(approval(), mode=Mode.Application, version=5)


def get_clear_src():
    return compileTeal(clear(), mode=Mode.Application, version=5)


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(get_approval_src())

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(get_clear_src())
