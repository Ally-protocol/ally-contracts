import os

import dotenv

from algosdk.future import transaction
from algosdk import encoding

from ally.account import Account
from ally.operations import destroy_pool
from ally.utils import get_algod_client, get_balances, wait_for_transaction


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator: {creator.get_address()}")

    app_id = int(os.environ.get("APP_ID"))
    
    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))

    version = 1
    threshold = 2
    
    msig = transaction.Multisig(
        version, 
        threshold, 
        [
            governor1.get_address(), 
            governor2.get_address(), 
            governor3.get_address()
        ]
    )
    
    if get_balances(client, msig.address())[0] < 200_000:
        pay_txn = transaction.PaymentTxn(
            sender=creator.get_address(),
            sp=client.suggested_params(),
            receiver=msig.address(),
            amt=200_000
        )
        signed_pay_txn = pay_txn.sign(creator.get_private_key())
        
        tx_id = client.send_transaction(signed_pay_txn)
        wait_for_transaction(client, tx_id)
    
    txn = transaction.ApplicationDeleteTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id
    )
    
    mtx = transaction.MultisigTransaction(txn, msig)
    
    mtx.sign(governor1.get_private_key())
    mtx.sign(governor3.get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)
