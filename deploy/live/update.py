import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from ally.operations.live.deploy import update
from ally.utils import get_algod_client
from algosdk.future import transaction


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    if(len(sys.argv) < 2):
        print("available contracts: [pool | ally]")
        exit(0)
    else:
        contract = sys.argv[1]
        app_id = int(os.environ.get(f"{contract.upper()}_APP_ID"))

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))

    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, governors)    
    update(contract, client, governors, app_id)
