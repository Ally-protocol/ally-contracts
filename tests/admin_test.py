import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List

from ally.account import Account
from ally.operations import set_governor
from ally.utils import get_algod_client

# TODO - transform this file into an assertion test follwing utils_test.py

# Include tests for admin/mint_price action
# Include tests for admin/redeem_price action
# Include tests for admin/set_governor action
# Include tests for admin/toggle_redeem action

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(
        os.environ.get("ALGOD_URL"), 
        os.environ.get("ALGOD_API_KEY")
    )

    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    app_id = int(os.environ.get("APP_ID"))

    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))

    version = 1
    threshold = 1
    
    set_governor(client, creator, app_id, [governor1, governor2, governor3], version, threshold)
