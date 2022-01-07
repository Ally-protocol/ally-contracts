import os

import dotenv
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from account import Account
from utils import wait_for_transaction, get_algod_client


def destroy_pool(client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationDeleteTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id
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
    
    destroy_pool(client, creator, app_id)
