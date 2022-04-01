"""
Purpose: manipulate the ally reward rate
Features: set & get
Actor: The current contract governor (admin)
When: setting the ally reward rate 
How: `python admin/ally_reward_rate.py --set 1_020_000_000`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from typing import List
from algosdk import encoding
from ally.account import Account
from ally.operations.dev.admin import set_ally_reward_rate
from ally.utils import get_algod_client, get_app_global_state
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

    state = get_app_global_state(client, app_id)
    current_ally_reward_rate = state[b"rr"]

    if len(sys.argv) >= 2 and sys.argv[1] == "--get":
        print(current_ally_reward_rate)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--set":
        new_ally_reward_rate = int(sys.argv[2])
        shift = (new_ally_reward_rate/current_ally_reward_rate)

        if shift == 1:
            print("ally reward rate is unchanged")
        else:
            set_ally_reward_rate(new_ally_reward_rate, client, funder, app_id)
    else:
        print("available actions:")
        print("\t--get \t\treturns the current ally reward rate price")
        print("\t--set VALUE \tsets the ally reward rate to the given value")
    