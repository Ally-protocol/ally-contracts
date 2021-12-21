from pyteal import *


class AllyPool:
    class Vars:
        owner_key = Bytes("owner")
        token_id_key = Bytes("token_id")
        total_mint_amount_key = Bytes("total_mint_amt")
        
    def on_create(self):
        return Seq(
            App.globalPut(self.Vars.owner_key, Txn.sender()),
            App.globalPut(self.Vars.total_mint_amount_key, Int(0)),
            Approve()
        )
        
    def on_bootstrap(self):
        token_id = App.globalGetEx(Int(0), self.Vars.token_id_key)
        return Seq(
            Assert(Txn.sender() == App.globalGet(self.Vars.owner_key)),
            token_id,
            Assert(token_id.hasValue() == Int(0)),
            
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: Int(0xFFFFFFFFFFFFFFFF),
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_unit_name: Bytes("wALGO"),
                TxnField.config_asset_name: Bytes("wALGO"),
                TxnField.config_asset_url: Bytes("https://maxos.studio"),
                TxnField.config_asset_manager: Global.zero_address(),
                TxnField.config_asset_clawback: Global.zero_address(),
                TxnField.config_asset_reserve: Global.zero_address(),
                TxnField.config_asset_freeze: Global.zero_address(),
            }),
            InnerTxnBuilder.Submit(),
            App.globalPut(self.Vars.token_id_key, InnerTxn.created_asset_id()),
            Approve()
        )
        
    def on_mint(self):
        mint_amount = ScratchVar(TealType.uint64)
        return Seq(
            Assert(
                And(
                    Txn.assets[0] == App.globalGet(self.Vars.token_id_key),
                    Global.group_size() >= Int(2),
                )
            ),
            Assert(Gtxn[0].type_enum() == TxnType.Payment),
            
            mint_amount.store(
                If(
                    App.globalGet(self.Vars.total_mint_amount_key) == Int(0),
                    Gtxn[0].amount(),
                    WideRatio(
                        [Balance(Global.current_application_address()), Gtxn[0].amount()], 
                        [App.globalGet(self.Vars.total_mint_amount_key)]
                    )
                )
            ),
            
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: mint_amount.load(),
            }),
            InnerTxnBuilder.Submit(),
            
            App.globalPut(
                self.Vars.total_mint_amount_key,
                App.globalGet(self.Vars.total_mint_amount_key) + mint_amount.load()
            ),
            Approve()
        )
        
    def on_redeem(self):
        return Seq(
            # TODO: 
            Approve()
        )
        
    def on_commit(self):
        return Seq(
            # TODO: 
            Approve()
        )
        
    def on_call(self):
        on_call_method = Txn.application_args[0]
        return Cond(
            [on_call_method == Bytes("bootstrap"), self.on_bootstrap()],
            [on_call_method == Bytes("mint"), self.on_mint()],
            [on_call_method == Bytes("redeem"), self.on_redeem()],
            [on_call_method == Bytes("commit"), self.on_commit()]
        )
        
    def approval_program(self):
        program = Cond(
            [Txn.application_id() == Int(0), self.on_create()],
            [
                Or(
                    Txn.on_completion() == OnComplete.OptIn,
                    Txn.on_completion() == OnComplete.DeleteApplication
                ),
                Approve()
            ],
            [Txn.on_completion() == OnComplete.NoOp, self.on_call()],
            [
                Or(
                    Txn.on_completion() == OnComplete.CloseOut,
                    Txn.on_completion() == OnComplete.UpdateApplication,
                ),
                Reject(),
            ],
        )
        return program

    def clear_state_program(self):
        return Approve()


if __name__ == '__main__':
    validator = AllyPool()
    with open('ally_validator_approval.teal', 'w') as f:
        compiled = compileTeal(validator.approval_program(),
                               mode=Mode.Application, version=5)
        f.write(compiled)

    with open('ally_validator_clear.teal', 'w') as f:
        compiled = compileTeal(
            validator.clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
