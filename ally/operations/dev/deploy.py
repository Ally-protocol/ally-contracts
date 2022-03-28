import random
from base64 import b64decode
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from ally.utils import wait_for_transaction, send_transaction
from ally.account import Account
from ally.contracts.pool import pool_approval_src, pool_clear_src
from ally.contracts.ally import ally_approval_src, ally_clear_src

def create(contract: str, client: AlgodClient, funder: Account):

    if(contract == "pool"):
        app_result = client.compile(pool_approval_src())
        clear_result = client.compile(pool_clear_src())

    if(contract == "ally"):
        app_result = client.compile(ally_approval_src())
        clear_result = client.compile(ally_clear_src())

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])

    global_schema = transaction.StateSchema(num_uints=32, num_byte_slices=32)
    local_schema = transaction.StateSchema(num_uints=8, num_byte_slices=8)

    txn = transaction.ApplicationCreateTxn(
        sender=funder.get_address(),
        sp=client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=app_bytes,
        clear_program=clear_bytes,
        global_schema=global_schema,
        local_schema=local_schema,
    )

    signed_txn = txn.sign(funder.get_private_key())
    tx_id = client.send_transaction(signed_txn)

    response = wait_for_transaction(client, tx_id)
    assert response.application_index is not None and response.application_index > 0
    return response.application_index


def bootstrap(client: AlgodClient, funder: Account, app_id: int):
    print(f"Sender: {funder.get_address()}")

    txn = transaction.ApplicationCallTxn(
        sender=funder.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"bootstrap"],
    )
    
    send_transaction(client, funder, txn)
    

def destroy(client: AlgodClient, funder: Account, app_id: int):
    print(f"Sender: {funder.get_address()}")
    
    txn = transaction.ApplicationDeleteTxn(
        sender=funder.get_address(),
        sp=client.suggested_params(),
        index=app_id
    )

    send_transaction(client, funder, txn)   
    

def update(contract: str, client: AlgodClient, funder: Account, app_id: int):

    if(contract == "pool"):
        app_result = client.compile(pool_approval_src())
        clear_result = client.compile(pool_clear_src())

    if(contract == "ally"):
        app_result = client.compile(ally_approval_src())
        clear_result = client.compile(ally_clear_src())

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])
    
    print(f"Sender: {funder.get_address()}")

    txn = transaction.ApplicationUpdateTxn(
        sender=funder.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        approval_program=app_bytes,
        clear_program=clear_bytes
    )

    send_transaction(client, funder, txn)
