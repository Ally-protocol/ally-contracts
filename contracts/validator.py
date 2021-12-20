from pyteal import *


class AllyValidator:
    class Vars:
        token_id_key = Bytes("token_id")
        
    def on_bootstrap(self):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: Int(0xFFFFFFFFFFFFFFFF),
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_unit_name: Bytes("wALGO"),
                TxnField.config_asset_name: Bytes("wALGO"),
                TxnField.config_asset_url: Bytes("https://www.maxos.studio"),
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
        return Seq(
            # TODO: 
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
            [
                Or(
                    Txn.application_id() == Int(0),
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
    validator = AllyValidator()
    with open('ally_validator_approval.teal', 'w') as f:
        compiled = compileTeal(validator.approval_program(),
                               mode=Mode.Application, version=5)
        f.write(compiled)

    with open('ally_validator_clear.teal', 'w') as f:
        compiled = compileTeal(
            validator.clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
