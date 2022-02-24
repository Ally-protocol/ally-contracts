import random
import json
from typing import List
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address
from algosdk import encoding

from ally.utils import is_opted_in_asset, is_opted_in_contract, wait_for_transaction
from ally.account import Account


def mint_walgo(client: AlgodClient, sender: Account, app_id: int, asset_id: int, amount: int):
    if not is_opted_in_contract(client, app_id, sender.get_address()):
        txn = transaction.ApplicationOptInTxn(
            sender=sender.get_address(),
            sp=client.suggested_params(),
            index=app_id
        )
        signed_txn = txn.sign(sender.get_private_key())
        client.send_transaction(signed_txn)

        wait_for_transaction(client, txn.get_txid())

    if not is_opted_in_asset(client, asset_id, sender.get_address()):
        txn = transaction.AssetOptInTxn(
            sender=sender.get_address(),
            sp=client.suggested_params(),
            index=asset_id
        )
        signed_txn = txn.sign(sender.get_private_key())
        client.send_transaction(signed_txn)

        wait_for_transaction(client, txn.get_txid())
        
    call_txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"mint"],
        foreign_assets=[asset_id]
    )
    payment_txn = transaction.PaymentTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        receiver=get_application_address(app_id),
        amt=amount + 1_000
    )
    
    transaction.assign_group_id([call_txn, payment_txn])
    
    signed_call_txn = call_txn.sign(sender.get_private_key())
    signed_payment_txn = payment_txn.sign(sender.get_private_key())
    
    tx_id = client.send_transactions([signed_call_txn, signed_payment_txn])
    
    wait_for_transaction(client, tx_id)
    
    
def redeem_walgo(client: AlgodClient, sender: Account, app_id: int, asset_id: int, amount: int):
    call_txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"redeem"],
        foreign_assets=[asset_id]
    )
    axfer_txn = transaction.AssetTransferTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        receiver=get_application_address(app_id),
        amt=amount,
        index=asset_id
    )

    transaction.assign_group_id([call_txn, axfer_txn])

    signed_call_txn = call_txn.sign(sender.get_private_key())
    signed_axfer_txn = axfer_txn.sign(sender.get_private_key())

    tx_id = client.send_transactions([signed_call_txn, signed_axfer_txn])

    wait_for_transaction(client, tx_id)


def claim_ally(client: AlgodClient, sender: Account, app_id: int, asset_id: int, pool_app_id: int):
    if not is_opted_in_contract(client, app_id, sender.get_address()):
        txn = transaction.ApplicationOptInTxn(
            sender=sender.get_address(),
            sp=client.suggested_params(),
            index=app_id
        )
        signed_txn = txn.sign(sender.get_private_key())
        client.send_transaction(signed_txn)

        wait_for_transaction(client, txn.get_txid())

    if not is_opted_in_asset(client, asset_id, sender.get_address()):
        txn = transaction.AssetOptInTxn(
            sender=sender.get_address(),
            sp=client.suggested_params(),
            index=asset_id
        )
        signed_txn = txn.sign(sender.get_private_key())
        client.send_transaction(signed_txn)

        wait_for_transaction(client, txn.get_txid())

    call_txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"claim"],
        foreign_assets=[asset_id],
        foreign_apps=[pool_app_id]
    )

    transaction.assign_group_id([call_txn])
    signed_call_txn = call_txn.sign(sender.get_private_key())
    tx_id = client.send_transactions([signed_call_txn])

    wait_for_transaction(client, tx_id)
