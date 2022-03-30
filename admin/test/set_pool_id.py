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
from ally.operations.test.admin import set_pool_id
from ally.utils import get_algod_client

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    pool_app_id = int(os.environ.get("POOL_APP_ID"))
    ally_app_id = int(os.environ.get("ALLY_APP_ID"))

    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    governor1 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR3_MNEMONIC"))
    governors = [governor1, governor2, governor3]

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))

    set_pool_id(pool_app_id, client, governors, ally_app_id, version, threshold)
    