import os
import dotenv
import pytest

from ally.account import Account
from ally.operations.user import mint_walgo, claim_ally
from ally.utils import get_algod_client, get_app_global_state, get_app_local_state, get_balances

from algosdk import error


dotenv.load_dotenv('.env')

client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
pool_app_id = int(os.environ.get("POOL_APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
ally_app_id = int(os.environ.get("ALLY_APP_ID"))
ally_id = int(os.environ.get("ALLY_ID"))
minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))
amount = 3_000_000

def test_claim():
    address = minter.get_address()
    print(f"minter: {address}")

    mint_walgo(client, minter, pool_app_id, walgo_id, amount)

    pool_local_state = get_app_local_state(client, pool_app_id, minter)
    allys_reward = pool_local_state[b"allys"]
    
    ally_local_state = get_app_local_state(client, ally_app_id, minter)
    allys_claimed = 0
    if "allys" in ally_local_state.keys():
        allys_claimed = ally_local_state[b"allys"]

    ally_to_claim = allys_reward > allys_claimed

    assert ally_to_claim > 0

    balances = get_balances(client, address)
    previous_allys = 0
    if ally_id in balances.keys():
        previous_allys = balances[ally_id]

    claim_ally(client, minter, ally_app_id, ally_id, pool_app_id)
    
    ally_local_state = get_app_local_state(client, ally_app_id, minter)
    allys_claimed = ally_local_state[b"allys"]

    assert allys_reward == allys_claimed
    
    balances = get_balances(client, address)
    current_allys = balances[ally_id]
    
    #assert current_allys - previous_allys == amount

