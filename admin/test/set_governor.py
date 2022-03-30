"""
Purpose: assign a new governor account
Actor: The current contract governor (admin)
When: changing the governor
How: `python admin/set_governor.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List

from ally.account import Account
from ally.operations.test.admin import set_governor
from ally.utils import get_algod_client


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(
        os.environ.get("ALGOD_URL"), 
        os.environ.get("ALGOD_API_KEY")
    )

    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    app_id = int(os.environ.get("POOL_APP_ID"))

    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    set_governor(client, creator, app_id, [governor1, governor2, governor3], version, threshold)