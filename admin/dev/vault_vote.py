"""
Purpose: manipulate vote action for Algorand governance
Actor: The current contract governor (admin)
When: voting to Algorand governance
How: `python admin/dev/vault_vote.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from ally.operations.dev.admin import vote_vault
from ally.utils import get_algod_client
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    walgo_id = int(os.environ.get("WALGO_ID"))

    vault1_id = int(os.environ.get("VAULT1_ID"))

    governance = os.environ.get("GOVERNANCE_ADDRESS")

    vote_vault(client, funder, vault1_id, walgo_id, governance)
    