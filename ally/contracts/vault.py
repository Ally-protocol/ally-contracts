import os

from pyteal import *

ONE_ALGO = 1_000_000
MIN_BALANCE = 110_000
TEAL_VERSION = 5

# Global State
governor_key = Bytes("gv")
pool_address_key = Bytes("pa")
pool_token_key = Bytes("pt")
redeem_price_key = Bytes("rp")
committed_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")

action_governor = Bytes("set_governor")
action_commit = Bytes("commit")
action_vote = Bytes("vote")
action_redeem = Bytes("redeem")
action_release = Bytes("release")

def approval():
    governor = App.globalGet(governor_key)

    # ALGOs to pay based on the burned wALGOs amount
    @Subroutine(TealType.uint64)
    def algos_to_redeem(amount):
        algos = WideRatio(
            [App.globalGet(redeem_price_key), amount],
            [Int(ONE_ALGO)]
        )
        return Seq(
            Return(algos)
        )

    # Function to make a payment transfer
    @Subroutine(TealType.none)
    def pay(receiver, amount):
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

    # Function to send whole ALGO back to pool app
    def release():
        contract_address = Global.current_application_address()
        pool_address = App.globalGet(pool_address_key)
        algo_balance = Balance(contract_address)

        return Seq(
            Assert(Txn.sender() == governor),
            Assert(algo_balance > Int(MIN_BALANCE)),
            pay(
                pool_address,
                algo_balance - Int(MIN_BALANCE)
            ),
            App.globalPut(allow_redeem_key, Int(0)),
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

    def commit():
        app_call = Gtxn[0]
        committed_algos = Btoi(Txn.application_args[2])
        redeem_price = Btoi(Txn.application_args[3])

        well_formed_commit = And(
            Global.group_size() == Int(1),
            app_call.type_enum() == TxnType.ApplicationCall,
            app_call.sender() == governor,
        )
        
        return Seq(
            Assert(well_formed_commit),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(0),
                    TxnField.note: Txn.application_args[1],
                }
            ),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_algos_key, committed_algos),
            App.globalPut(allow_redeem_key, Int(1)),
            App.globalPut(redeem_price_key, redeem_price),
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
            Assert(well_formed_vote),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(0),
                    TxnField.note: Txn.application_args[1],
                }
            ),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    # Function to redeem users' walgo tokens - user action
    def redeem():
        contract_address = Global.current_application_address()
        pool_address = App.globalGet(pool_address_key)
        pool_token = App.globalGet(pool_token_key)
        algo_balance = Balance(contract_address)
        app_call = Gtxn[0]
        asset_xfer = Gtxn[1]
        redeem_amount = algos_to_redeem(asset_xfer.asset_amount())
        return Seq(
            Assert(App.globalGet(allow_redeem_key)),
            Assert(
                And(
                    Global.group_size() == Int(2),
                    app_call.type_enum() == TxnType.ApplicationCall,
                    app_call.assets[0] == pool_token,
                    asset_xfer.type_enum() == TxnType.AssetTransfer,
                    asset_xfer.sender() == app_call.sender(),
                    asset_xfer.asset_receiver() == pool_address,
                    asset_xfer.xfer_asset() == pool_token,
                    algo_balance > redeem_amount
                )
            ),
            pay(
                asset_xfer.sender(),
                algos_to_redeem(asset_xfer.asset_amount())
            ),
            Approve(),
        )

    # Initialize the Global State on creation
    handle_creation = Seq(
        App.globalPut(governor_key, Txn.sender()),
        App.globalPut(committed_algos_key, Int(0)),
        App.globalPut(allow_redeem_key, Int(0)),
        App.globalPut(redeem_price_key, Int(ONE_ALGO)),
        App.globalPut(pool_address_key, Txn.accounts[1]),
        App.globalPut(pool_token_key, Btoi(Txn.application_args[0])),
        Approve()
    )

    # Routes the NoOp to the corresponding action based on the first app param
    router = Seq(
        Assert(Txn.close_remainder_to() == Global.zero_address()),
        Assert(Txn.asset_close_to() == Global.zero_address()),
        Assert(Txn.rekey_to() == Global.zero_address()),
        Cond(
            [Txn.application_args[0] == action_governor, set_governor()],
            [Txn.application_args[0] == action_commit, commit()],
            [Txn.application_args[0] == action_vote, vote()],
            [Txn.application_args[0] == action_redeem, redeem()],
            [Txn.application_args[0] == action_release, release()],
        )
    )

    # Routes the OnComplete actions to the corresponding action
    return Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Txn.sender() == governor)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Txn.sender() == governor)],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.NoOp, router],
    )


def clear():
    return Approve()

# Compiling functions
def vault_approval_src():
    return compileTeal(approval(), mode=Mode.Application, version=TEAL_VERSION)

def vault_clear_src():
    return compileTeal(clear(), mode=Mode.Application, version=TEAL_VERSION)

# When executing this file, compile this PyTeal into TEAL
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(vault_approval_src())

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(vault_clear_src())
