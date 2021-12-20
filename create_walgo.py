import os
import dotenv

from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from account import Account
from utils import get_algod_client, wait_for_transaction


def create_walgo(client: AlgodClient, creator: Account):
    txn = transaction.AssetCreateTxn(
        sender=creator.get_address(),
        sp=client.suggested_params(),
        total=10_000_000_000_000_000,
        decimals=6,
        default_frozen=False,
        manager=creator.get_address(),
        reserve=creator.get_address(),
        freeze=creator.get_address(),
        clawback=creator.get_address(),
        unit_name="wALGO",
        asset_name="wALGO",
        url="https://www.maxos.studio/"
    )

    signed_txn = txn.sign(creator.get_private_key())

    client.send_transaction(signed_txn)

    res = wait_for_transaction(client, signed_txn.get_txid())

    assert res.asset_index is not None and res.asset_index > 0
    return res.asset_index


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    algod_url = os.environ.get("ALGOD_URL")
    algod_api_key = os.environ.get("ALGOD_API_KEY")
    client = get_algod_client(algod_url, algod_api_key)
    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator's address: {creator.get_address()}")
    walgo_id = create_walgo(client, creator)
    print(f"wALGO ID: {walgo_id}")
