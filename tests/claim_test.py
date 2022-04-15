import pytest

from ally.account import Account
from ally.environment import Env
from ally.action.user import mint_walgo, claim_ally
from ally.utils import get_app_local_state, get_balances

amount = 3_000_000

def test_claim():
    env = Env()

    minter = env.minter
    address = minter.get_address()
    print(f"minter: {address}")

    mint_walgo(minter, amount)

    pool_local_state = get_app_local_state(env.client, env.pool_app_id, minter)
    allys_reward = pool_local_state[b"allys"]
    
    ally_local_state = get_app_local_state(env.client, env.ally_app_id, minter)
    allys_claimed = 0
    if "allys" in ally_local_state.keys():
        allys_claimed = ally_local_state[b"allys"]

    ally_to_claim = allys_reward > allys_claimed

    assert ally_to_claim > 0

    balances = get_balances(env.client, address)
    previous_allys = 0
    if env.ally_asa_id in balances.keys():
        previous_allys = balances[env.ally_asa_id]

    claim_ally(minter)
    
    ally_local_state = get_app_local_state(env.client, env.ally_app_id, minter)
    allys_claimed = ally_local_state[b"allys"]

    assert allys_reward == allys_claimed
    
    balances = get_balances(env.client, address)
    current_allys = balances[env.ally_asa_id]
    
    #assert current_allys - previous_allys == amount

