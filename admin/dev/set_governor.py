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

from algosdk.future import transaction

from ally.account import Account
from ally.operations.dev.admin import set_multisig_governor
from ally.utils import get_algod_client


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(
        os.environ.get("ALGOD_URL"), 
        os.environ.get("ALGOD_API_KEY")
    )

    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    app_id = int(os.environ.get("POOL_APP_ID"))

    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))

    msig = transaction.Multisig(
        version, threshold, 
        [governor1, governor2, governor3]
    )
    
    set_multisig_governor(client, creator, app_id, msig)
