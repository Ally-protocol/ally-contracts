from ally.environment import Env
from ally.action.admin import set_mint_price, set_redeem_price, set_ally_reward_rate, set_ally_price, set_pool_id, toggle_redeem
from ally.utils import get_app_global_state

env = Env()

def test_mint_price():
    state = get_app_global_state(env.client, env.pool_app_id)
    current_mint_price = state[b"mp"]
    new_mint_price = current_mint_price + 1_000

    assert current_mint_price > 0

    set_mint_price(new_mint_price)
    state = get_app_global_state(env.client, env.pool_app_id)
    current_mint_price = state[b"mp"]

    assert new_mint_price == current_mint_price

def test_redeem_price():
    state = get_app_global_state(env.client, env.pool_app_id)
    current_redeem_price = state[b"rp"]
    new_redeem_price = current_redeem_price - 1_000

    assert current_redeem_price > 0

    set_redeem_price(new_redeem_price)
    state = get_app_global_state(env.client, env.pool_app_id)
    current_redeem_price = state[b"rp"]

    assert new_redeem_price == current_redeem_price

def test_set_ally_price():
    state = get_app_global_state(env.client, env.ally_app_id)
    previous_ally_price = state[b"pc"]
    new_ally_price = previous_ally_price + 1_000

    assert previous_ally_price > 0

    set_ally_price(new_ally_price)
    state = get_app_global_state(env.client, env.ally_app_id)
    current_ally_price = state[b"pc"]

    assert new_ally_price == current_ally_price

def test_ally_reward_rate():
    state = get_app_global_state(env.client, env.pool_app_id)
    current_ally_reward_rate = state[b"rr"]
    new_ally_reward_rate = current_ally_reward_rate + 1_000

    assert current_ally_reward_rate > 0

    set_ally_reward_rate(new_ally_reward_rate)
    state = get_app_global_state(env.client, env.pool_app_id)
    current_ally_reward_rate = state[b"rr"]

    assert new_ally_reward_rate == current_ally_reward_rate

def test_toggle_redeem():
    state = get_app_global_state(env.client, env.pool_app_id)
    redeem_state = state[b"ar"]
    toggle_redeem()

    state = get_app_global_state(env.client, env.pool_app_id)
    new_redeem_state = state[b"ar"]

    assert redeem_state == 1 - new_redeem_state
    
    # set it back for further tests
    toggle_redeem()
