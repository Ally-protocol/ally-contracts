import os

import dotenv
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from account import Account
from utils import get_algod_client, wait_for_transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    
    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    
    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    
    app_id = int(os.environ.get("APP_ID"))

    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))

    version = 1
    threshold = 2
    msig = transaction.Multisig(
        version, threshold, [governor1.get_address(), governor2.get_address()])
    
    print('multisig address: ', msig.address())
    
    txn = transaction.ApplicationCallTxn(
        sender=creator.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=[b"set_governor"],
        accounts=[msig.address()],
        on_complete=transaction.OnComplete.NoOpOC
    )
    signed_txn = txn.sign(creator.get_private_key())
    
    client.send_transaction(signed_txn)
    
    wait_for_transaction(client, signed_txn.get_txid())
