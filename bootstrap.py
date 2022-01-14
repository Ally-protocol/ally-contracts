import os

import dotenv

from ally.account import Account
from ally.operations import bootstrap_pool
from ally.utils import get_algod_client, get_app_global_state
    

if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get(
        "ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    creator = Account.from_mnemonic(os.environ.get("CREATOR_MNEMONIC"))
    print(f"Creator: {creator.get_address()}")

    app_id = int(os.environ.get("APP_ID"))
    
    bootstrap_pool(client, creator, app_id)
    
    state = get_app_global_state(client, app_id)
    
    print("Global state: ", state)

