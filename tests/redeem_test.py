import pytest

from ally.environment import Env
from ally.account import Account
from ally.action.user import redeem_walgo
from ally.action.admin import toggle_redeem
from ally.utils import get_app_global_state, get_balances

from algosdk import error

PRECISION = 1_000_000
FEE = 1000
amount = 1_000_000

env = Env()

def test_redeem():
    minter = env.minter
    address = minter.get_address()
    print(f"minter: {address}")

    redeem_price = get_app_global_state(env.client, env.pool_app_id)[b"rp"]
    mint_price = get_app_global_state(env.client, env.pool_app_id)[b"mp"]

    balances = get_balances(env.client, address)
    previous_algo  = balances[0]
    previous_walgo = 0

    if env.walgo_asa_id in balances.keys():
        previous_walgo = balances[env.walgo_asa_id]

    assert previous_walgo > 0
    print(f"previous_walgo: {previous_walgo}")

    redeem_walgo(minter, previous_walgo)

    balances = get_balances(env.client, address)
    current_algo  = balances[0]
    current_walgo = balances[env.walgo_asa_id]

    expected_redeem_algo = int(float((previous_walgo * redeem_price) / PRECISION))
    print(f"redeem price: {redeem_price}")
    print(f"mint price: {mint_price}")

    assert current_walgo == 0
    assert current_algo == previous_algo - FEE * 2 + expected_redeem_algo

def test_disabled_redeem():
    minter = env.minter
    address = minter.get_address()
    print(f"minter: {address}")

    # disable redeem
    toggle_redeem()

    with pytest.raises(error.AlgodHTTPError) as txn_info:
        redeem_walgo(minter, amount)
    assert "logic eval error: assert failed" in str(txn_info.value)

    # enable it back
    toggle_redeem()
