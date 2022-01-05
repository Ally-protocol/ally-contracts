import os
import dotenv
from typing import Tuple

from base64 import b64decode
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk.logic import get_application_address

from contracts.pool import get_approval_src, get_clear_src
from utils import wait_for_transaction, get_algod_client
from account import Account


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


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator: {creator.get_address()}")

    app_id = create_pool(client, creator)

    print(f"App ID: {app_id}")
    print(f"App address: {get_application_address(app_id)}")
