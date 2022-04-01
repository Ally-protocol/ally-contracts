"""
Purpose: enable/disable wALGO token redemption
Actor: the current contract governor (admin)
When: the redeem period starts or ends
How: `python admin/toggle_redeem.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.operations.live.admin import toggle_redeem
from ally.utils import get_algod_client
from algosdk.future import transaction


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    
    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, governors)

    toggle_redeem(client, msig, app_id)
    