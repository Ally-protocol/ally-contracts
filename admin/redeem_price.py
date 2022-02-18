"""
Purpose: manipulate the redeem price
Features: set & get
Actor: The current contract governor (admin)
When: setting the redeem price 
How: `python admin/redeem_price.py --set 1_020_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List
from algosdk import encoding
from ally.account import Account
from ally.operations import set_redeem_price
from ally.utils import get_algod_client, get_app_global_state
from algosdk.future import transaction

ALLOWED_SHIFT = 2.5 # percent

MIN = 1 - ALLOWED_SHIFT/100
MAX = 1 + ALLOWED_SHIFT/100

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("APP_ID"))
    version = 1
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    governor1 = Account.from_mnemonic(os.environ.get("GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("GOVERNOR3_MNEMONIC"))
    governors = [governor1, governor2, governor3]

    state = get_app_global_state(client, app_id)
    current_redeem_price = state[b"rp"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        state = get_app_global_state(client, app_id)
        current_redeem_price = state[b"rp"]
        print(current_redeem_price)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_redeem_price = int(sys.argv[2])
        shift = (new_redeem_price/current_redeem_price)

        if shift == 1:
            print("redeem price is unchanged")
        elif (shift >= MIN and shift <= MAX) or (len(sys.argv) >= 4 and sys.argv[3] == "--force"):
            set_redeem_price(new_redeem_price, client, governors, app_id, version, threshold)
        else:
            print("the shift when setting the redeem value should not be greater than 2.5%")
            print("if you meant this, add --force at the end of the command")
    else:
        print("available actions:")
        print("\t--get \t\treturns the current redeem price")
        print("\t--set VALUE \tsets the redeem price to the given value")
    