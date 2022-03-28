"""
Purpose: manipulate the maximum mint amount per transaction
Features: set & get
Actor: The current contract governor (admin)
When: setting the max mint
How: `python admin/max_mint.py --set 10_000_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.operations.live.admin import set_max_mint
from ally.utils import get_algod_client, get_app_global_state
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, [governor.get_address() for governor in governors])    

    state = get_app_global_state(client, app_id)
    current_max_mint = state[b"mm"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        print(current_max_mint)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_max_mint = int(sys.argv[2])
        set_max_mint(new_max_mint, client, msig, app_id)
    else:
        print("available actions:")
        print("\t--get \t\treturns the current maximum mint amount per transaction")
        print("\t--set VALUE \tsets the maximum mint amount to the given value")
    