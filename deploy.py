import os
import dotenv

from algosdk.logic import get_application_address

from ally.operations import create_pool
from ally.utils import get_algod_client
from ally.account import Account


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator: {creator.get_address()}")

    app_id = create_pool(client, creator)

    print(f"App ID: {app_id}")
    print(f"App address: {get_application_address(app_id)}")
