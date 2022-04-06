"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: committing to Algorand governance
How: `python admin/live/commit.py 3_000_000 1_003_000 950_000 10`
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

    msig = transaction.Multisig(version, threshold, governors)    

    governance = os.environ.get("GOVERNANCE_ADDRESS")

    if len(sys.argv) == 5:
        commit_amount = int(sys.argv[1])
        new_mint_price = int(sys.argv[2])
        new_redeem_price = int(sys.argv[3])
        new_fee_percent = int(sys.argv[4])

        commit(commit_amount, client, msig, app_id, walgo_id, governance, new_mint_price, new_redeem_price, new_fee_percent)
    else:
        print("Invalid argument counts!")
    