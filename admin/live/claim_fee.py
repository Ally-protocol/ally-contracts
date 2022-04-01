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

from ally.operations.live.admin import claim_fee
from ally.utils import get_algod_client
from algosdk.logic import get_application_address
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    pool_app_id = int(os.environ.get("POOL_APP_ID"))
    ally_app_id = int(os.environ.get("ALLY_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, governors)    

    ally_address = get_application_address(ally_app_id)

    claim_fee(client, msig, pool_app_id, walgo_id, ally_address)
