import os
import dotenv
import pytest

from ally.account import Account
from ally.operations import redeem_walgo, toggle_redeem
from ally.utils import get_algod_client, get_app_global_state, get_governors, get_balances

from algosdk import error

PRECISION = 1_000_000_000
FEE = 1000

dotenv.load_dotenv('.env')

client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
app_id = int(os.environ.get("APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))

version = 1
threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
governors = get_governors()

amount = 10_000_000

def test_redeem():
    address = minter.get_address()
    print(f"minter: {address}")

    redeem_price = get_app_global_state(client, app_id)[b"rp"]

    balances = get_balances(client, address)
    previous_algo  = balances[0]
    previous_walgo = 0
    if walgo_id in balances.keys():
        previous_walgo = balances[walgo_id]

    redeem_walgo(client, minter, app_id, walgo_id, amount)

    balances = get_balances(client, address)
    current_algo  = balances[0]
    current_walgo = balances[walgo_id]

    current_minus_redeemed = int(current_algo - (amount * redeem_price)/PRECISION)

    assert previous_walgo == current_walgo + amount
    assert (previous_algo - current_minus_redeemed) <= (FEE*2) # 2 transactions


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
