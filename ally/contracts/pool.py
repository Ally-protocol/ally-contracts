import os

from pyteal import *

TOTAL_SUPPLY = 0xFFFFFFFFFFFFFFFF
ONE_ALGO = 1_000_000
INITIAL_FUNDING = ONE_ALGO
PRECISION = 1_000_000
FEE = 1_000
TEAL_VERSION = 6

# Global State
governor_key = Bytes("gv")
pool_token_key = Bytes("pt")
mint_price_key = Bytes("mp")
redeem_price_key = Bytes("rp")
committed_algos_key = Bytes("co")
allow_redeem_key = Bytes("ar")
ally_reward_rate_key = Bytes("rr")
fee_percentage_key = Bytes("fp")
last_commit_price_key = Bytes("lc")
max_mint_key = Bytes("mm")
promised_allys_key = Bytes("pa")

# Local State
allys_key = Bytes("allys")

action_governor = Bytes("set_governor")
action_boot = Bytes("bootstrap")
action_mint_price = Bytes("set_mint_price")
action_redeem_price = Bytes("set_redeem_price")
action_ally_reward_rate = Bytes("set_ally_reward_rate")
action_fee_percentage = Bytes("set_fee_percentage")
action_max_mint = Bytes("set_max_mint")
action_last_commit_price = Bytes("set_last_commit_price")
action_claim_fee = Bytes("claim_fee")
action_toggle = Bytes("toggle_redeem")
action_commit = Bytes("commit")
action_vote = Bytes("vote")
action_mint = Bytes("mint")
action_redeem = Bytes("redeem")


def approval():
    governor = App.globalGet(governor_key)

    # Amount of walgos to mint based on the paid algos
    @Subroutine(TealType.uint64)
    def walgos_to_mint(algos):
        amount = WideRatio(
            [Int(ONE_ALGO), algos, Int(PRECISION)],
            [App.globalGet(mint_price_key), Int(PRECISION)]
        )
        return Seq(
            Return(amount)
        )

    # ALGOs to pay based on the burned wALGOs amount
    @Subroutine(TealType.uint64)
    def algos_to_redeem(amount):
        algos = WideRatio(
            [App.globalGet(redeem_price_key), amount, Int(PRECISION)],
            [Int(ONE_ALGO), Int(PRECISION)]
        )
        return Seq(
            Return(algos)
        )

    # ALLYs to reward based on the ally reward rate
    @Subroutine(TealType.uint64)
    def allys_to_reward(amount):
        allys = WideRatio(
            [App.globalGet(ally_reward_rate_key), amount, Int(PRECISION)],
            [Int(ONE_ALGO), Int(PRECISION)]
        )
        return Seq(
            Return(allys)
        )

    # Get ratio of ALGO/wALGO
    @Subroutine(TealType.uint64)
    def algo_walgo_ratio():
        contract_address = Global.current_application_address()
        pool_token = App.globalGet(pool_token_key)
        algo_balance = Balance(contract_address)
        pool_balance = AssetHolding.balance(contract_address, pool_token)

        return Seq(
            pool_balance,
            If(
                Int(TOTAL_SUPPLY) > pool_balance.value(),
                Return(
                    WideRatio(
                        [algo_balance - Int(INITIAL_FUNDING), Int(ONE_ALGO), Int(PRECISION)],
                        [Int(TOTAL_SUPPLY) - pool_balance.value(), Int(PRECISION)]
                    )
                ),
                Return(
                    Int(ONE_ALGO)
                )
            )
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
                    TxnField.receiver: receiver,
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

    # Function to send fee funds to allys address passed by
    # param in foreign accounts array - admin action
    def claim_fee():
        contract_address = Global.current_application_address()
        ally_address = Txn.accounts[1]
        algo_balance = Balance(contract_address)
        current_ratio = algo_walgo_ratio()
        fee_percentage = App.globalGet(fee_percentage_key)
        last_commit_price = App.globalGet(last_commit_price_key)
        amount = WideRatio(
            [fee_percentage, algo_balance, current_ratio - last_commit_price, Int(PRECISION)],
            [Int(ONE_ALGO), Int(100), Int(PRECISION)]
        )

        return Seq(
            Assert(Txn.sender() == governor),
            Assert(current_ratio > last_commit_price),
            Assert(algo_balance > Int(1_000)),
            Assert(amount > Int(1_000)),
            pay(ally_address, amount),
            App.globalPut(mint_price_key, algo_walgo_ratio()),
            App.globalPut(redeem_price_key, algo_walgo_ratio()),
            App.globalPut(ally_reward_rate_key, Int(0)),
            Approve()
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
        new_mint_price = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            Assert(new_mint_price > algo_walgo_ratio()),
            App.globalPut(mint_price_key, new_mint_price),
            Approve()
        )

    # Function to set a new redeem price - admin action
    def set_redeem_price():
        new_redeem_price = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            Assert(new_redeem_price < algo_walgo_ratio()),
            App.globalPut(redeem_price_key, new_redeem_price),
            Approve()
        )

    # Function to set a new ally reward rate - admin action
    def set_ally_reward_rate():
        new_ally_reward_rate = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(ally_reward_rate_key, new_ally_reward_rate),
            Approve()
        )

    # Function to set a new fee percentage - admin action
    def set_fee_percentage():
        new_fee_percentage = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            Assert(new_fee_percentage > Int(0)),
            Assert(new_fee_percentage <= Int(30)),
            App.globalPut(fee_percentage_key, new_fee_percentage),
            Approve()
        )

    # Function to set a the maximum mint amount per transaction - admin action
    def set_max_mint():
        new_max_mint = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(max_mint_key, new_max_mint),
            Approve()
        )
        
    # Function to set a the maximum mint amount per transaction - admin action
    def set_last_commit_price():
        new_last_commit_price = Btoi(Txn.application_args[1])
        return Seq(
            Assert(Txn.sender() == governor),
            App.globalPut(last_commit_price_key, new_last_commit_price),
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
        committed_algos = Btoi(Txn.application_args[2])
        new_mint_price = Btoi(Txn.application_args[3])
        new_redeem_price = Btoi(Txn.application_args[4])
        new_fee_percentage = Btoi(Txn.application_args[5])

        well_formed_commit = And(
            Global.group_size() == Int(1),
            app_call.type_enum() == TxnType.ApplicationCall,
            app_call.sender() == governor,
            new_mint_price > algo_walgo_ratio(),
            new_redeem_price < algo_walgo_ratio(),
            new_fee_percentage > Int(0),
            new_fee_percentage <= Int(30),
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
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
            App.globalPut(committed_algos_key, committed_algos),
            App.globalPut(last_commit_price_key, algo_walgo_ratio()),
            App.globalPut(mint_price_key, new_mint_price),
            App.globalPut(redeem_price_key, new_redeem_price),
            App.globalPut(fee_percentage_key, new_fee_percentage),
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

    # Function to mint new walgo tokens - user action
    def mint():
        contract_address = Global.current_application_address()
        pool_token = App.globalGet(pool_token_key)
        pool_balance = AssetHolding.balance(contract_address, pool_token)
        app_call = Gtxn[0]
        payment = Gtxn[1]
        # calculates the walgos amount
        walgos_amount = walgos_to_mint(payment.amount() - Int(FEE))
        # calculates ally reward
        ally_amount = allys_to_reward(walgos_amount)
        ally_reward = ally_amount + App.localGet(Int(0), allys_key)
        promised_allys = ally_amount + App.globalGet(promised_allys_key)
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
                    payment.amount() > Int(FEE),
                    payment.amount() <= App.globalGet(max_mint_key) + Int(FEE),
                )
            ),
            axfer(
                payment.sender(),
                pool_token,
                walgos_amount
            ),
            App.globalPut(promised_allys_key, promised_allys),
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
                algos_to_redeem(asset_xfer.asset_amount()) - Int(FEE)
            ),
            Approve(),
        )

    # Initialize the Global State on creation
    handle_creation = Seq(
        App.globalPut(mint_price_key, Int(ONE_ALGO)),
        App.globalPut(redeem_price_key, Int(ONE_ALGO)),
        App.globalPut(last_commit_price_key, Int(ONE_ALGO)),
        App.globalPut(fee_percentage_key, Int(10)),
        App.globalPut(max_mint_key, Int(10_000_000)),
        App.globalPut(allow_redeem_key, Int(1)),
        App.globalPut(ally_reward_rate_key, Int(0)),
        App.globalPut(committed_algos_key, Int(0)),
        App.globalPut(promised_allys_key, Int(0)),
        App.globalPut(governor_key, Txn.sender()),
        Approve()
    )

    # Routes the NoOp to the corresponding action based on the first app param
    router = Seq(
        Assert(Txn.close_remainder_to() == Global.zero_address()),
        Assert(Txn.asset_close_to() == Global.zero_address()),
        Assert(Txn.rekey_to() == Global.zero_address()),
        Cond(
            [Txn.application_args[0] == action_boot, bootstrap()],
            [Txn.application_args[0] == action_governor, set_governor()],
            [Txn.application_args[0] == action_mint_price, set_mint_price()],
            [Txn.application_args[0] == action_redeem_price, set_redeem_price()],
            [Txn.application_args[0] == action_ally_reward_rate, set_ally_reward_rate()],
            [Txn.application_args[0] == action_fee_percentage, set_fee_percentage()],
            [Txn.application_args[0] == action_max_mint, set_max_mint()],
            [Txn.application_args[0] == action_last_commit_price, set_last_commit_price()],
            [Txn.application_args[0] == action_claim_fee, claim_fee()],
            [Txn.application_args[0] == action_toggle, toggle_redeem()],
            [Txn.application_args[0] == action_commit, commit()],
            [Txn.application_args[0] == action_vote, vote()],
            [Txn.application_args[0] == action_mint, mint()],
            [Txn.application_args[0] == action_redeem, redeem()],
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
def pool_approval_src():
    return compileTeal(approval(), mode=Mode.Application, version=TEAL_VERSION)

def pool_clear_src():
    return compileTeal(clear(), mode=Mode.Application, version=TEAL_VERSION)

# When executing this file, compile this PyTeal into TEAL
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(pool_approval_src())

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(pool_clear_src())
