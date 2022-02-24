import os
import dotenv

from typing import List
from algosdk.future import transaction
from algosdk import encoding

from ally.account import Account
from ally.operations.admin import set_mint_price, set_redeem_price, set_ally_reward_rate, toggle_redeem, set_governor, set_multisig_governor
from ally.utils import get_algod_client, get_app_global_state, get_governors


dotenv.load_dotenv('.env')
client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
app_id = int(os.environ.get("POOL_APP_ID"))
version = 1
threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
governors = get_governors()

def test_mint_price():
    state = get_app_global_state(client, app_id)
    current_mint_price = state[b"mp"]
    new_mint_price = current_mint_price + 1_000

    assert current_mint_price > 0

    set_mint_price(new_mint_price, client, governors, app_id, version, threshold)

    state = get_app_global_state(client, app_id)
    current_mint_price = state[b"mp"]
    assert new_mint_price == current_mint_price

    # set it back to 1 for further testing
    set_mint_price(1_000_000_000, client, governors, app_id, version, threshold)

def test_redeem_price():
    state = get_app_global_state(client, app_id)
    current_redeem_price = state[b"rp"]
    new_redeem_price = current_redeem_price + 1_000

    assert current_redeem_price > 0

    set_redeem_price(new_redeem_price, client, governors, app_id, version, threshold)

    state = get_app_global_state(client, app_id)
    current_redeem_price = state[b"rp"]
    assert new_redeem_price == current_redeem_price

    # set it back to 1 for further testing
    set_redeem_price(1_000_000_000, client, governors, app_id, version, threshold)

def test_ally_reward_rate():
    state = get_app_global_state(client, app_id)
    current_ally_reward_rate = state[b"rr"]
    new_ally_reward_rate = current_ally_reward_rate + 1_000

    assert current_ally_reward_rate > 0

    set_ally_reward_rate(new_ally_reward_rate, client, governors, app_id, version, threshold)

    state = get_app_global_state(client, app_id)
    current_ally_reward_rate = state[b"rr"]
    assert new_ally_reward_rate == current_ally_reward_rate

def test_toggle_redeem():
    state = get_app_global_state(client, app_id)
    redeem_state = state[b"ar"]

    toggle_redeem(client, governors, app_id, version, threshold)

    state = get_app_global_state(client, app_id)
    new_redeem_state = state[b"ar"]

    assert redeem_state == 1 - new_redeem_state
    
    # set it back for further tests
    toggle_redeem(client, governors, app_id, version, threshold)

def test_set_governor_as_funder():
    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
    set_governor(client, creator, app_id, governors, version, threshold)

    state = get_app_global_state(client, app_id)
    new_governor = state[b"gv"]

    assert creator.get_address() == encoding.encode_address(new_governor)

def test_set_governor_as_multisig():
    creator = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    msig = transaction.Multisig(
        version, threshold, 
        [governor.get_address() for governor in governors]
    )
    
    set_multisig_governor(client, creator, app_id, msig)

    state = get_app_global_state(client, app_id)
    new_governor = state[b"gv"]

    assert msig.address() == encoding.encode_address(new_governor)

