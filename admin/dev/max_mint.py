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

from ally.account import Account
from ally.operations.dev.admin import set_max_mint
from ally.utils import get_algod_client, get_app_global_state
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    state = get_app_global_state(client, app_id)
    current_max_mint = state[b"mm"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        print(current_max_mint)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_max_mint = int(sys.argv[2])
        set_max_mint(new_max_mint, client, funder, app_id)
    else:
        print("available actions:")
        print("\t--get \t\treturns the current maximum mint amount per transaction")
        print("\t--set VALUE \tsets the maximum mint amount to the given value")
    