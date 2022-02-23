import os

from pyteal import *

TOTAL_SUPPLY = 0xFFFFFFFFFFFFFFFF
ONE_ALGO_IN_MICRO = 1_000_000_000 # TODO test with 1M
VERSION = 5

# Global State
governor_key = Bytes("gv")
pool_token_key = Bytes("pt")
mint_price_key = Bytes("mp")
redeem_price_key = Bytes("rp")
committed_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")
ally_reward_rate_key = Bytes("rr")

# Local State
allys_key = Bytes("allys")

action_governor = Bytes("set_governor")
action_boot = Bytes("bootstrap")
action_mint_price = Bytes("set_mint_price")
action_redeem_price = Bytes("set_redeem_price")
action_ally_reward_rate = Bytes("set_ally_reward_rate")
action_toggle = Bytes("toggle_redeem")
action_commit = Bytes("commit")
action_vote = Bytes("vote")
action_mint = Bytes("mint")
action_redeem = Bytes("redeem")


def approval():
    governor = App.globalGet(governor_key)

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

    # ALLYs to reward based on the ally reward rate
    @Subroutine(TealType.uint64)
    def allys_to_reward(amount: TealType.uint64):
        allys = WideRatio(
            [App.globalGet(ally_reward_rate_key), amount],
            [Int(ONE_ALGO_IN_MICRO)]
        )
        return Seq(
            Return(allys)
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

    # Function to set a new ally reward rate - admin action
    def set_ally_reward_rate():
        new_ally_reward_rate = Txn.application_args[1]
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(ally_reward_rate_key, Btoi(new_ally_reward_rate)),
            Approve()
        )

    # Function to enable/disable redemption - admin action
    def toggle_redeem():
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(allow_redeem_key, Not(App.globalGet(allow_redeem_key))),
            Approve()
        )

    def commit():
        app_call = Gtxn[0]
        well_formed_commit = And(
            Global.group_size() == Int(1),
            app_call.type_enum() == TxnType.ApplicationCall,
            app_call.sender() == governor,
        )

        committed_algos = App.globalGet(committed_algos_key) + Btoi(Txn.application_args[2])
        
        return Seq(
            Assert(well_formed_commit),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(0),
                    TxnField.note: Txn.application_args[1],
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_algos_key, committed_algos),
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
        # calculates the walgos amount
        walgos_amount = walgos_to_mint(payment.amount() - Int(1_000)) # TODO use payment.fee()
        # calculates ally reward
        ally_amount = allys_to_reward(walgos_amount)
        ally_reward = ally_amount + App.localGet(Int(0), allys_key)
        return Seq(
            pool_balance,
            Assert(
                And(
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
                walgos_amount
            ),
            App.localPut(Int(0), allys_key, ally_reward),
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
        App.globalPut(ally_reward_rate_key, Int(ONE_ALGO_IN_MICRO)),
        App.globalPut(allow_redeem_key, Int(1)),
        App.globalPut(committed_algos_key, Int(0)),
        App.globalPut(governor_key, Txn.sender()),
        Approve()
    )

    # Routes the NoOp to the corresponding action based on the first app param
    router = Cond(
        [Txn.application_args[0] == action_boot, bootstrap()],
        [Txn.application_args[0] == action_governor, set_governor()],
        [Txn.application_args[0] == action_mint_price, set_mint_price()],
        [Txn.application_args[0] == action_redeem_price, set_redeem_price()],
        [Txn.application_args[0] == action_ally_reward_rate, set_ally_reward_rate()],
        [Txn.application_args[0] == action_toggle, toggle_redeem()],
        [Txn.application_args[0] == action_commit, commit()],
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
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.NoOp, router],
    )


def clear():
    return Approve()

# Compiling functions
def pool_approval_src():
    return compileTeal(approval(), mode=Mode.Application, version=VERSION)

def pool_clear_src():
    return compileTeal(clear(), mode=Mode.Application, version=VERSION)

# When executing this file, compile this PyTeal into TEAL
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(pool_approval_src())

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(pool_clear_src())
