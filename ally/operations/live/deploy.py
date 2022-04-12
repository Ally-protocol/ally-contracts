import os
import random
from base64 import b64decode
from typing import List
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk import encoding

from ally.utils import wait_for_transaction
from ally.account import Account
from ally.contracts.pool import pool_approval_src, pool_clear_src
from ally.contracts.ally import ally_approval_src, ally_clear_src
from ally.contracts.vault import vault_approval_src, vault_clear_src

def create(contract: str, client: AlgodClient, governors: List[Account], multisig_threshold: int):

    if(contract == "pool"):
        app_result = client.compile(pool_approval_src())
        clear_result = client.compile(pool_clear_src())

    if(contract == "ally"):
        app_result = client.compile(ally_approval_src())
        clear_result = client.compile(ally_clear_src())

    if(contract == "vault"):
        app_result = client.compile(vault_approval_src())
        clear_result = client.compile(vault_clear_src())

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])

    global_schema = transaction.StateSchema(num_uints=32, num_byte_slices=32)
    local_schema = transaction.StateSchema(num_uints=8, num_byte_slices=8)
    
    msig = transaction.Multisig(
        1, multisig_threshold, 
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCreateTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=app_bytes,
        clear_program=clear_bytes,
        global_schema=global_schema,
        local_schema=local_schema,
    )
    mtx = transaction.MultisigTransaction(txn, msig)
    
    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())
    
    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    response = wait_for_transaction(client, tx_id)
    assert response.application_index is not None and response.application_index > 0
    return response.application_index


def bootstrap(client: AlgodClient, governors: List[Account], multisig_threshold: int, app_id: int):
    msig = transaction.Multisig(
        1, multisig_threshold, 
        [governor.get_address() for governor in governors]
    )
    print(f"Sender: {msig.address()}")

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"bootstrap"],
    )
    mtx = transaction.MultisigTransaction(txn, msig)
    
    signers = random.choices(governors, k=multisig_threshold)
    for signer in signers:
        mtx.sign(signer.get_private_key())
    
    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))
    
    wait_for_transaction(client, tx_id)
    

def destroy(client: AlgodClient, governors: List[Account], multisig_threshold: int, app_id: int):
    msig = transaction.Multisig(
        1, multisig_threshold, 
        [governor.get_address() for governor in governors]
    )
    print(f"Sender: {msig.address()}")
    
    txn = transaction.ApplicationDeleteTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id
    )
    mtx = transaction.MultisigTransaction(txn, msig)
    
    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())
    
    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))
    
    wait_for_transaction(client, tx_id)
    

def update(contract: str, client: AlgodClient, msig: transaction.Multisig, app_id: int):

    if(contract == "pool"):
        app_result = client.compile(pool_approval_src())
        clear_result = client.compile(pool_clear_src())

    if(contract == "ally"):
        app_result = client.compile(ally_approval_src())
        clear_result = client.compile(ally_clear_src())

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])
    
    print(f"Sender: {msig.address()}")

    txn = transaction.ApplicationUpdateTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        approval_program=app_bytes,
        clear_program=clear_bytes
    )
    mtx = transaction.MultisigTransaction(txn, msig)
    save_mtx_file(mtx)

def save_mtx_file(mtx: transaction.MultisigTransaction):
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, 'tx_files')

    filename = '/unsigned.mtx'

    transaction.write_to_file(
        [mtx], file_path + filename)
