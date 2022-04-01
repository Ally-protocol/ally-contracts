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

from typing import List

from ally.account import Account
from ally.operations.dev.admin import toggle_redeem
from ally.utils import get_algod_client
from algosdk.future import transaction


if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    toggle_redeem(client, funder, app_id)
    