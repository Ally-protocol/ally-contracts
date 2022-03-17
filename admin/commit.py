"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: committing to Algorand governance
How: `python admin/commit_price.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from ally.operations.admin import commit
from ally.utils import get_algod_client

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))
    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))

    governance = os.environ.get("GOVERNANCE_ADDRESS")
    
    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))
    governors = [governor1, governor2, governor3]
    commit_amount = 1_000_000

    commit(commit_amount, client, governors, app_id, threshold, governance, walgo_id)
    