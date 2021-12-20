from pyteal import *


class AllyValidator:
    class Vars:
        token_id_key = Bytes("token_id")
        
    def on_create(self):
        token_id = Btoi(Txn.application_args[0])
        return Seq(
            App.globalPut(self.Vars.token_id_key, token_id),
            Approve()
        )
        
    def on_setup(self):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: App.globalGet(self.Vars.token_id_key),
                TxnField.asset_receiver: Global.current_application_address()
            }),
            InnerTxnBuilder.Submit(),
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
            [on_call_method == Bytes("setup"), self.on_setup()],
            [on_call_method == Bytes("mint"), self.on_mint()],
            [on_call_method == Bytes("redeem"), self.on_redeem()],
            [on_call_method == Bytes("commit"), self.on_commit()]
        )
        
    def approval_program(self):
        program = Cond(
            [Txn.application_id() == Int(0), self.on_create()],
            [Txn.on_completion() == OnComplete.NoOp, self.on_call()],
            [
                Or(
                    Txn.on_completion() == OnComplete.OptIn,
                    Txn.on_completion() == OnComplete.DeleteApplication
                ),
                Approve()
            ],
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
