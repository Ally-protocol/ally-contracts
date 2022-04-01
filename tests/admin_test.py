import os
import dotenv

from typing import List
from algosdk.future import transaction
from algosdk import encoding

from ally.account import Account
from ally.operations.dev.admin import set_mint_price, set_redeem_price, set_ally_reward_rate, set_ally_price, set_pool_id, toggle_redeem, set_governor, set_multisig_governor
from ally.utils import get_algod_client, get_app_global_state, get_governors


dotenv.load_dotenv('.env')
client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
pool_app_id = int(os.environ.get("POOL_APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
ally_app_id = int(os.environ.get("ALLY_APP_ID"))
funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))

def test_mint_price():
    state = get_app_global_state(client, pool_app_id)
    current_mint_price = state[b"mp"]
    new_mint_price = current_mint_price + 1_000

    assert current_mint_price > 0

    set_mint_price(new_mint_price, client, funder, pool_app_id, walgo_id)

    state = get_app_global_state(client, pool_app_id)
    current_mint_price = state[b"mp"]
    assert new_mint_price == current_mint_price

def test_redeem_price():
    state = get_app_global_state(client, pool_app_id)
    current_redeem_price = state[b"rp"]
    new_redeem_price = current_redeem_price - 1_000

    assert current_redeem_price > 0

    set_redeem_price(new_redeem_price, client, funder, pool_app_id, walgo_id)

    state = get_app_global_state(client, pool_app_id)
    current_redeem_price = state[b"rp"]
    assert new_redeem_price == current_redeem_price

def test_set_ally_price():
    state = get_app_global_state(client, ally_app_id)
    previous_ally_price = state[b"pc"]
    new_ally_price = previous_ally_price + 1_000

    assert previous_ally_price > 0

    set_ally_price(new_ally_price, client, funder, ally_app_id)

    state = get_app_global_state(client, ally_app_id)
    current_ally_price = state[b"pc"]
    assert new_ally_price == current_ally_price

def test_set_pool_id():
    state = get_app_global_state(client, ally_app_id)
    previous_pool_id = state[b"pl"]
    new_pool_id = pool_app_id

    assert previous_pool_id > 0

    set_pool_id(new_pool_id, client, funder, ally_app_id)

    state = get_app_global_state(client, ally_app_id)
    current_pool_id = state[b"pl"]
    assert new_pool_id == current_pool_id

def test_ally_reward_rate():
    state = get_app_global_state(client, pool_app_id)
    current_ally_reward_rate = state[b"rr"]
    new_ally_reward_rate = current_ally_reward_rate + 1_000

    assert current_ally_reward_rate > 0

    set_ally_reward_rate(new_ally_reward_rate, client, funder, pool_app_id)

    state = get_app_global_state(client, pool_app_id)
    current_ally_reward_rate = state[b"rr"]
    assert new_ally_reward_rate == current_ally_reward_rate

def test_toggle_redeem():
    state = get_app_global_state(client, pool_app_id)
    redeem_state = state[b"ar"]

    toggle_redeem(client, funder, pool_app_id)

    state = get_app_global_state(client, pool_app_id)
    new_redeem_state = state[b"ar"]

    assert redeem_state == 1 - new_redeem_state
    
    # set it back for further tests
    toggle_redeem(client, funder, pool_app_id)
