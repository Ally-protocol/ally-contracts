from base64 import b64decode
from typing import List, Tuple
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address

from .utils import wait_for_transaction
from .account import Account
from .contracts.pool import get_approval_src, get_clear_src


def fullyCompileContract(client: AlgodClient, teal: str) -> bytes:
    response = client.compile(teal)
    return b64decode(response["result"])


def get_contracts(client: AlgodClient) -> Tuple[bytes, bytes]:
    approval_program = fullyCompileContract(
        client, get_approval_src())
    clear_state_program = fullyCompileContract(
        client, get_clear_src())

    return approval_program, clear_state_program


def create_pool(client: AlgodClient, creator: Account):
    approval, clear = get_contracts(client)
    global_schema = transaction.StateSchema(num_uints=32, num_byte_slices=32)
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    txn = transaction.ApplicationCreateTxn(
        sender=creator.get_address(),
        sp=client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=global_schema,
        local_schema=local_schema,
    )
    signed_txn = txn.sign(creator.get_private_key())
    client.send_transaction(signed_txn)

    response = wait_for_transaction(client, signed_txn.get_txid())
    assert response.application_index is not None and response.application_index > 0
    return response.application_index


def bootstrap_pool(client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"bootstrap"],
    )
    signed_txn = txn.sign(sender.get_private_key())
    client.send_transaction(signed_txn)
    
    wait_for_transaction(client, signed_txn.get_txid())
    
    
def set_governor(client: AlgodClient, sender: Account, app_id: int, governors: List[Account], version: int, threshold: int):
    msig = transaction.Multisig(
        version, threshold, [governor.get_address() for governor in governors]
    )

    print('multisig address: ', msig.address())

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=[b"set_governor"],
        accounts=[msig.address()],
        on_complete=transaction.OnComplete.NoOpOC
    )
    signed_txn = txn.sign(sender.get_private_key())

    client.send_transaction(signed_txn)

    wait_for_transaction(client, signed_txn.get_txid())
    
    
def destroy_pool(client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationDeleteTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id
    )
    signed_txn = txn.sign(sender.get_private_key())

    client.send_transaction(signed_txn)

    wait_for_transaction(client, signed_txn.get_txid())
    
    
def mint_walgo(client: AlgodClient, sender: Account, app_id: int, amount: int):
    call_txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=[b"mint"]
    )
    payment_txn = transaction.PaymentTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        receiver=get_application_address(app_id),
        amt=amount
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
        app_args=[b"redeem"]
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
