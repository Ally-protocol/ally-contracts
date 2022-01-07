import os

import dotenv
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from account import Account
from utils import get_algod_client, get_app_global_state, wait_for_transaction


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
    

if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator: {creator.get_address()}")

    app_id = int(os.environ.get("APP_ID"))
    
    # bootstrap_pool(client, creator, app_id)
    
    state = get_app_global_state(client, app_id)
    
    print("Global state: ", state)

