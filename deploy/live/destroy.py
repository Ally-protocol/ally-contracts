import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from ally.operations.live.deploy import destroy
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

    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governors = [governor1, governor2, governor3]    
    
    destroy(client, governors, threshold, app_id)
