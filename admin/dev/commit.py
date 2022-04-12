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

from ally.account import Account
from ally.operations.dev.admin import commit
from ally.utils import get_algod_client
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    app_id = int(os.environ.get("POOL_APP_ID"))

    if len(sys.argv) == 5:
        commit_amount = int(sys.argv[1])
        new_mint_price = int(sys.argv[2])
        new_redeem_price = int(sys.argv[3])
        new_fee_percent = int(sys.argv[4])

        commit(client, funder, app_id, new_mint_price, new_redeem_price, new_fee_percent)
    else:
        print("Invalid argument counts!")
    