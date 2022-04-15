from algosdk import encoding
from algosdk.future import transaction
from ally.utils import wait_for_transaction
from .account import Account
import random

def process_txn(env, txn):    
    print(f"SENDER: {env.sender}")
    if env.autosign:
        return send_txn(env, txn)
    else:
        save_txn(env, txn)
            
def send_txn(env, txn):
    if env.multisig:
        governors = []
        mtx = transaction.MultisigTransaction(txn, env.msig)
        for i in random.sample(range(0, len(env.gov_pks)), env.threshold):
            mtx.sign(env.gov_pks[i])
        tx_id = env.client.send_raw_transaction(encoding.msgpack_encode(mtx))
    else:
        signed_txn = txn.sign(env.signer_pk)
        tx_id = env.client.send_transaction(signed_txn)
    
    return wait_for_transaction(env.client, tx_id)
    
def save_txn(env, txn):
    if env.multisig:
        txn = transaction.MultisigTransaction(txn, env.msig)
    transaction.write_to_file([txn], env.output + 'unsigned.txn')
