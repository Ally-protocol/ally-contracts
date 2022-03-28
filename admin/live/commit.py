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


from ally.operations.live.admin import commit
from ally.utils import get_algod_client
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, [governor.get_address() for governor in governors])    

    governance = os.environ.get("GOVERNANCE_ADDRESS")
    commit_amount = 1_000_000

    commit(commit_amount, client, msig, app_id, threshold, governance, walgo_id)
    