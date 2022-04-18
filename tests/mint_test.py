from ally.account import Account
from ally.environment import Env
from ally.action.user import mint_walgo
from ally.utils import get_app_global_state, get_app_local_state, get_balances

PRECISION = 1_000_000
FEE = 1000

env = Env()

def test_mint():
    minter = env.minter
    address = minter.get_address()
    print(f"minter: {address}")

    global_state = get_app_global_state(env.client, env.pool_app_id)
    local_state = get_app_local_state(env.client, env.pool_app_id, minter)
    balances = get_balances(env.client, address)

    mint_price = global_state[b"mp"]
    print(f"fee: {mint_price}")

    ally_reward_rate = global_state[b"rr"]
    previous_allys = 0

    if "allys" in local_state.keys():
        previous_allys = local_state[b"allys"]

    previous_algo  = balances[0]
    previous_walgo = 0
    transaction_count = 4

    if env.walgo_asa_id in balances.keys():
        previous_walgo = balances[env.walgo_asa_id]
        transaction_count = 3

    amount = 1_000_000

    mint_walgo(minter, amount)

    local_state = get_app_local_state(env.client, env.pool_app_id, minter)
    balances = get_balances(env.client, address)

    current_allys = local_state[b"allys"]
    current_algo  = balances[0]
    current_walgo = balances[env.walgo_asa_id]

    expect_minted_walgo = int((amount * PRECISION) / mint_price)

    assert current_walgo == previous_walgo + expect_minted_walgo 
    assert current_algo == previous_algo - amount - FEE * transaction_count

