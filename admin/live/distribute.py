"""
Purpose: send allys to the account sent by parameter
Actor: The current contract governor (admin)
When: sending allys or doing airdrops
How: `python admin/distribute.py ACX...ASR 3_000_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.operations.live.admin import distribute
from ally.utils import get_algod_client
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    ally_app_id = int(os.environ.get("ALLY_APP_ID"))

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")
    governors = [governor1, governor2, governor3]

    msig = transaction.Multisig(version, threshold, governors)

    send_to = sys.argv[1]
    amount = int(sys.argv[2])

    distribute(ally_app_id, client, msig, send_to, amount)
    