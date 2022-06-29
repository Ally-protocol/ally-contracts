import os
from pyteal import *

TOTAL_SUPPLY = 1_000_000_000_000_000
ONE_ALGO = 1_000_000
TEAL_VERSION = 6
FEE = 1_000
TIME_DELAY = Int(604_800) # 7 days

# Global State
governor_key = Bytes("gv")
token_key = Bytes("tk")
pool_id_key = Bytes("pl")
set_pool_key = Bytes("sp")
price_key = Bytes("pc")
claimed_allys_key = Bytes("ca")

# time delay
approval_app_key = Bytes("ap")
clear_app_key = Bytes("cp")
request_time_key = Bytes("rt")

# Local State
allys_key = Bytes("allys")

action_boot = Bytes("bootstrap")
action_governor = Bytes("set_governor")
action_pool_id = Bytes("set_pool_id")
action_price = Bytes("set_price")
action_claim = Bytes("claim")
action_sell = Bytes("sell")
action_distribute = Bytes("distribute")
action_governor = Bytes("set_governor")
action_update_request = Bytes("update_request")
action_update_execution = Bytes("update_execution")


def approval():
    governor = App.globalGet(governor_key)

    # ALGOs to pay based on allys price
    @Subroutine(TealType.uint64)
    def algos_to_pay(ally_amount):
        algos = WideRatio(
            [App.globalGet(price_key), ally_amount],
            [Int(ONE_ALGO)]
        )
        return Seq(
            Return(algos)
        )

    # Function to make an asset transfer
    @Subroutine(TealType.none)
    def axfer(receiver, asset_id, amount):
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

    # Function to boot the app after creation - sets up ally asset
    def bootstrap():
        contract_address = Global.current_application_address()
        token_check = App.globalGetEx(Int(0), token_key)
        return Seq(
            token_check,
            # Make sure we've not already set this
            Assert(Not(token_check.hasValue())),
            Assert(Txn.sender() == governor),
            # Create ally token
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Bytes("ALLY"),
                TxnField.config_asset_unit_name: Bytes("ALLY"),
                TxnField.config_asset_url: Bytes("https://www.allyprotocol.com"),
                TxnField.config_asset_total: Int(TOTAL_SUPPLY),
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_manager: contract_address,
                TxnField.config_asset_reserve: contract_address,
            }),
            InnerTxnBuilder.Submit(),
            # Write it to global state
            App.globalPut(token_key, InnerTxn.created_asset_id()),
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

    # Function to set the pool id - admin action
    def set_pool_id():
        new_pool_id = Txn.application_args[1]
        return Seq(
            Assert(Txn.sender() == governor),
            Assert(Not(App.globalGet(set_pool_key))),
            App.globalPut(pool_id_key, Btoi(new_pool_id)),
            App.globalPut(set_pool_key, Int(1)),
            Approve()
        )

    # Function to set the sell price - admin action
    def set_price():
        new_price = Txn.application_args[1]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(price_key, Btoi(new_price)),
            Approve()
        )

    # Function to claim ally tokens - user action
    def claim():
        contract_address = Global.current_application_address()
        token = App.globalGet(token_key)
        balance = AssetHolding.balance(contract_address, token)
        sender = Txn.accounts[0]
        pool_app = Txn.applications[1]
        # gets the ally to claim amount (ally_rewards - ally_claimed)
        ally_rewards = App.localGetEx(sender, pool_app, allys_key)
        ally_claimed = App.localGet(Int(0), allys_key)

        return Seq(
            balance,
            ally_rewards,
            Assert(
                And(
                    ally_rewards.value() > ally_claimed,
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.assets[0] == token,
                    App.globalGet(pool_id_key) == pool_app
                )
            ),
            axfer(
                sender,
                token,
                ally_rewards.value() - ally_claimed
            ),
            App.globalPut(claimed_allys_key, App.globalGet(claimed_allys_key) + (ally_rewards.value() - ally_claimed)),
            App.localPut(Int(0), allys_key, ally_rewards.value()),
            Approve(),
        )


    def distribute():
        contract_address = Global.current_application_address()
        token = App.globalGet(token_key)
        balance = AssetHolding.balance(contract_address, token)

        address_to = Txn.accounts[1]
        amount = Btoi(Txn.application_args[1])

        return Seq(
            balance,
            Assert(
                And(
                    Txn.sender() == governor,
                    amount > Int(0),
                    Txn.type_enum() == TxnType.ApplicationCall,
                    Txn.assets[0] == token,
                )
            ),
            axfer(address_to, token, amount),
            Approve(),
        )

    
    # Function to sell users' ally tokens - user action
    def sell():
        contract_address = Global.current_application_address()
        token = App.globalGet(token_key)
        balance = AssetHolding.balance(contract_address, token)
        app_call = Gtxn[0]
        asset_xfer = Gtxn[1]
        return Seq(
            Assert(
                And(
                    Global.group_size() == Int(2),
                    app_call.type_enum() == TxnType.ApplicationCall,
                    app_call.assets[0] == token,
                    asset_xfer.type_enum() == TxnType.AssetTransfer,
                    asset_xfer.sender() == app_call.sender(),
                    asset_xfer.asset_receiver() == contract_address,
                    asset_xfer.xfer_asset() == token,
                )
            ),
            balance,
            pay(
                asset_xfer.sender(),
                algos_to_pay(asset_xfer.asset_amount()) - Int(FEE)
            ),
            Approve(),
        )

    # Function to redeem users' walgo tokens - user action
    def request_update_contract():
        approval_app = Txn.application_args[1]
        clear_app = Txn.application_args[2]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(approval_app_key, approval_app),
            App.globalPut(clear_app_key, clear_app),
            App.globalPut(request_time_key, Global.latest_timestamp()),
            Approve(),
        )

    # Initialize the Global State on creation
    handle_creation = Seq(
        App.globalPut(governor_key, Txn.sender()),
        App.globalPut(price_key, Int(ONE_ALGO)),
        App.globalPut(claimed_allys_key, Int(0)),
        App.globalPut(set_pool_key, Int(0)),
        App.globalPut(request_time_key, Int(0)),
        Approve()
    )

    # Time delay to update contract
    handle_update = Seq(
        Assert(Txn.sender() == governor),
        Assert(App.globalGet(request_time_key) > Int(0)),
        Assert(Global.latest_timestamp() - App.globalGet(request_time_key) > TIME_DELAY),
        Assert(Txn.application_args[0] == App.globalGet(approval_app_key)), # args[0] includes SHA-256 hash value of approval app
        Assert(Txn.application_args[1] == App.globalGet(clear_app_key)), # args[1] includes SHA-256 hash value of clear app
        App.globalPut(request_time_key, Int(0)),
        Approve()
    )

    # Routes the NoOp to the corresponding action based on the first app param
    router = Seq(
        Cond(
            [Txn.application_args[0] == action_boot, bootstrap()],
            [Txn.application_args[0] == action_governor, set_governor()],
            [Txn.application_args[0] == action_pool_id, set_pool_id()],
            [Txn.application_args[0] == action_price, set_price()],
            [Txn.application_args[0] == action_claim, claim()],
            [Txn.application_args[0] == action_distribute, distribute()],
            [Txn.application_args[0] == action_governor, set_governor()],
            [Txn.application_args[0] == action_sell, Reject()], #sell()],
            [Txn.application_args[0] == action_update_request, request_update_contract()],
        )
    )

    # Routes the OnComplete actions to the corresponding action
    return Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Txn.sender() == governor)],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_update],
        [Txn.on_completion() == OnComplete.CloseOut, Reject()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.NoOp, router],
    )


def clear():
    return Reject()

# Compiling functions
def ally_approval_src():
    return compileTeal(approval(), mode=Mode.Application, version=TEAL_VERSION)

def ally_clear_src():
    return compileTeal(clear(), mode=Mode.Application, version=TEAL_VERSION)

# When executing this file, compile this PyTeal into TEAL
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(ally_approval_src())

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(ally_clear_src())
