"""
Purpose: manipulate the fee percentage used when claiming (sending) the fee to the ally treasure
Features: set & get
Actor: The current contract governor (admin)
When: setting the fee percentage
How: `python admin/fee_percentage.py --set 300_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List
from algosdk import encoding
from ally.account import Account
from ally.operations.admin import set_fee_percentage
from ally.utils import get_algod_client, get_app_global_state
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))
    governors = [governor1, governor2, governor3]

    state = get_app_global_state(client, app_id)
    current_fee_percentage = state[b"fp"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        print(current_fee_percentage)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_fee_percentage = int(sys.argv[2])
        set_fee_percentage(new_fee_percentage, client, governors, app_id, version, threshold)
    else:
        print("available actions:")
        print("\t--get \t\treturns the current fee percentage")
        print("\t--set VALUE \tsets the fee percentage to the given value")
    