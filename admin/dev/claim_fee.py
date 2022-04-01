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

from typing import List
from algosdk import encoding
from ally.account import Account
from ally.operations.dev.admin import claim_fee
from ally.utils import get_algod_client, get_app_global_state
from algosdk.logic import get_application_address
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    pool_app_id = int(os.environ.get("POOL_APP_ID"))
    ally_app_id = int(os.environ.get("ALLY_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    ally_address = get_application_address(ally_app_id)

    claim_fee(client, funder, pool_app_id, walgo_id, ally_address)
