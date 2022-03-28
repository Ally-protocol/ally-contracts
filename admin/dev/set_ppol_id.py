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

from ally.account import Account
from ally.operations.dev.admin import set_pool_id
from ally.utils import get_algod_client

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    pool_app_id = os.environ.get("POOL_APP_ID")
    ally_app_id = os.environ.get("ALLY_APP_ID")

    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    if not pool_app_id:
        print("Please deploy pool app first:")
    elif not ally_app_id:
        print("Please deploy ally app:")
    else:
        set_pool_id(int(pool_app_id), client, funder, int(ally_app_id))
    