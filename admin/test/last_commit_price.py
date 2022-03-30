"""
Purpose: manipulate the last commit price
Features: set & get
Actor: The current contract governor (admin)
When: setting the last commit price
How: `python admin/last_commit_price.py --set 10_000_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List
from algosdk import encoding
from ally.account import Account
from ally.operations.test.admin import set_last_commit_price
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
    current_last_commit_price = state[b"lc"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        print(current_last_commit_price)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_last_commit_price = int(sys.argv[2])
        set_last_commit_price(new_last_commit_price, client, governors, app_id, version, threshold)
    else:
        print("available actions:")
        print("\t--get \t\treturns the last commit price")
        print("\t--set VALUE \tsets the last commit price to the given value")
    