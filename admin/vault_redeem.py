"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: committing to Algorand governance
How: `python admin/dev/vault_commit.py 3_000_000 950_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.account import Account
from tests.action.user import mint_walgo, redeem_vault
from ally.utils import get_algod_client
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    pool_id = int(os.environ.get("POOL_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))

    vault1_id = int(os.environ.get("VAULT1_ID"))

    governance = os.environ.get("GOVERNANCE_ADDRESS")

    algo_amount = 1_000_000

    mint_walgo(client, funder, pool_id, walgo_id, algo_amount)
    redeem_vault(client, funder, pool_id, vault1_id, walgo_id, algo_amount)
    