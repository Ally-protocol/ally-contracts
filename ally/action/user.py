from algosdk.future import transaction
from algosdk.logic import get_application_address
from ally.environment import Env

from ally.utils import is_opted_in_asset, is_opted_in_contract, wait_for_transaction, send_transaction
from ally.account import Account

env = Env()

def mint_walgo(minter: Account, amount: int):
    if not is_opted_in_contract(env.client, env.pool_app_id, minter.get_address()):
        txn = transaction.ApplicationOptInTxn(
            sender=minter.get_address(),
            sp=env.client.suggested_params(),
            index=env.pool_app_id
        )
        send_transaction(env.client, minter, txn)

    if not is_opted_in_asset(env.client, env.walgo_asa_id, minter.get_address()):
        txn = transaction.AssetOptInTxn(
            sender=minter.get_address(),
            sp=env.client.suggested_params(),
            index=env.walgo_asa_id
        )
        send_transaction(env.client, minter, txn)
        
    call_txn = transaction.ApplicationCallTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"mint"],
        foreign_assets=[env.walgo_asa_id]
    )
    payment_txn = transaction.PaymentTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        receiver=get_application_address(env.pool_app_id),
        amt=amount + 1_000
    )
    
    transaction.assign_group_id([call_txn, payment_txn])
    
    signed_call_txn = call_txn.sign(minter.get_private_key())
    signed_payment_txn = payment_txn.sign(minter.get_private_key())

    tx_id = env.client.send_transactions([signed_call_txn, signed_payment_txn])
    wait_for_transaction(env.client, tx_id)
    
    
def redeem_walgo(minter: Account, amount: int):
    call_txn = transaction.ApplicationCallTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"redeem"],
        foreign_assets=[env.walgo_asa_id]
    )
    axfer_txn = transaction.AssetTransferTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        receiver=env.pool_app_address,
        amt=amount,
        index=env.walgo_asa_id
    )

    transaction.assign_group_id([call_txn, axfer_txn])

    signed_call_txn = call_txn.sign(minter.get_private_key())
    signed_axfer_txn = axfer_txn.sign(minter.get_private_key())

    tx_id = env.client.send_transactions([signed_call_txn, signed_axfer_txn])
    wait_for_transaction(env.client, tx_id)


def redeem_vault(minter: Account,vault_id: int, amount: int):
    call_txn = transaction.ApplicationCallTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        index=vault_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"redeem"],
        foreign_assets=[env.walgo_asa_id]
    )
    axfer_txn = transaction.AssetTransferTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        receiver=env.pool_app_address,
        amt=amount,
        index=env.walgo_asa_id
    )

    transaction.assign_group_id([call_txn, axfer_txn])

    signed_call_txn = call_txn.sign(minter.get_private_key())
    signed_axfer_txn = axfer_txn.sign(minter.get_private_key())

    tx_id = env.client.send_transactions([signed_call_txn, signed_axfer_txn])
    wait_for_transaction(env.client, tx_id)


def claim_ally(minter: Account):
    if not is_opted_in_contract(env.client, env.ally_app_id, minter.get_address()):
        txn = transaction.ApplicationOptInTxn(
            sender=minter.get_address(),
            sp=env.client.suggested_params(),
            index=env.ally_app_id
        )
        send_transaction(env.client, minter, txn)

    if not is_opted_in_asset(env.client, env.ally_asa_id, minter.get_address()):
        txn = transaction.AssetOptInTxn(
            sender=minter.get_address(),
            sp=env.client.suggested_params(),
            index=env.ally_asa_id
        )
        send_transaction(env.client, minter, txn)

    call_txn = transaction.ApplicationCallTxn(
        sender=minter.get_address(),
        sp=env.client.suggested_params(),
        index=env.ally_app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"claim"],
        foreign_assets=[env.ally_asa_id],
        foreign_apps=[env.pool_app_id]
    )

    transaction.assign_group_id([call_txn])
    signed_call_txn = call_txn.sign(minter.get_private_key())
    tx_id = env.client.send_transactions([signed_call_txn])

    wait_for_transaction(env.client, tx_id)
