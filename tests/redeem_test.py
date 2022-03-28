import os

from pyteal import WideRatio
import dotenv
import pytest

from ally.account import Account
from ally.operations.user import redeem_walgo
from ally.operations.test.admin import toggle_redeem
from ally.utils import get_algod_client, get_app_global_state, get_governors, get_balances

from algosdk import error

PRECISION = 1_000_000
FEE = 1000

dotenv.load_dotenv('.env')

client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
app_id = int(os.environ.get("POOL_APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))

version = 1
threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
governors = get_governors()

amount = 1_000_000

def test_redeem():
    address = minter.get_address()
    print(f"minter: {address}")

    redeem_price = get_app_global_state(client, app_id)[b"rp"]
    mint_price = get_app_global_state(client, app_id)[b"mp"]

    balances = get_balances(client, address)
    previous_algo  = balances[0]
    previous_walgo = 0
    if walgo_id in balances.keys():
        previous_walgo = balances[walgo_id]

    assert previous_walgo > 0
    print(f"previous_walgo: {previous_walgo}")

    redeem_walgo(client, minter, app_id, walgo_id, previous_walgo)

    balances = get_balances(client, address)
    current_algo  = balances[0]
    current_walgo = balances[walgo_id]

    expected_redeem_algo = int((previous_walgo * redeem_price) / PRECISION)
    print(f"redeem price: {redeem_price}")
    print(f"mint price: {mint_price}")

    assert current_walgo == 0
    assert current_algo == previous_algo - FEE * 2 + expected_redeem_algo

def test_disabled_redeem():
    address = minter.get_address()
    print(f"minter: {address}")

    # disable redeem
    toggle_redeem(client, governors, app_id, version, threshold)

    with pytest.raises(error.AlgodHTTPError) as txn_info:
        redeem_walgo(client, minter, app_id, walgo_id, amount)
    assert "logic eval error: assert failed" in str(txn_info.value)

    # enable it back
    toggle_redeem(client, governors, app_id, version, threshold)
