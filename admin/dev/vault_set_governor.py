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
from ally.operations.dev.admin import set_governor_1_to_M
from ally.utils import get_algod_client


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(
        os.environ.get("ALGOD_URL"), 
        os.environ.get("ALGOD_API_KEY")
    )

    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    vault1_id = int(os.environ.get("VAULT1_ID"))
    vault2_id = int(os.environ.get("VAULT2_ID"))
    vault3_id = int(os.environ.get("VAULT3_ID"))
    vault4_id = int(os.environ.get("VAULT4_ID"))
    vault5_id = int(os.environ.get("VAULT5_ID"))
    vault6_id = int(os.environ.get("VAULT6_ID"))
    vault7_id = int(os.environ.get("VAULT7_ID"))
    vault8_id = int(os.environ.get("VAULT8_ID"))
    vault9_id = int(os.environ.get("VAULT9_ID"))
    vault10_id = int(os.environ.get("VAULT10_ID"))
    vault11_id = int(os.environ.get("VAULT11_ID"))
    vault12_id = int(os.environ.get("VAULT12_ID"))

    governor1 = os.environ.get("GOVERNOR1")
    governor2 = os.environ.get("GOVERNOR2")
    governor3 = os.environ.get("GOVERNOR3")

    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))

    msig = transaction.Multisig(
        version, threshold, 
        [governor1, governor2, governor3]
    )
    
    set_governor_1_to_M(client, creator, vault1_id, msig)
    set_governor_1_to_M(client, creator, vault2_id, msig)
    set_governor_1_to_M(client, creator, vault3_id, msig)
    set_governor_1_to_M(client, creator, vault4_id, msig)
    set_governor_1_to_M(client, creator, vault5_id, msig)
    set_governor_1_to_M(client, creator, vault6_id, msig)
    set_governor_1_to_M(client, creator, vault7_id, msig)
    set_governor_1_to_M(client, creator, vault8_id, msig)
    set_governor_1_to_M(client, creator, vault9_id, msig)
    set_governor_1_to_M(client, creator, vault10_id, msig)
    set_governor_1_to_M(client, creator, vault11_id, msig)
    set_governor_1_to_M(client, creator, vault12_id, msig)
