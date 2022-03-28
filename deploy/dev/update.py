import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from ally.operations.dev.deploy import update
from ally.utils import get_algod_client


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    if(len(sys.argv) < 2):
        print("available contracts: [pool | ally]")
        exit(0)
    else:
        contract = sys.argv[1]
        app_id = int(os.environ.get(f"{contract.upper()}_APP_ID"))

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    
    update(contract, client, funder, app_id)
