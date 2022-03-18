import os
import dotenv

from ally.account import Account
from ally.operations.user import mint_walgo
from ally.utils import get_algod_client, get_app_global_state, get_app_local_state, get_balances

PRECISION = 1_000_000
FEE = 1000

dotenv.load_dotenv('.env')

client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
app_id = int(os.environ.get("POOL_APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))


def test_mint():
    address = minter.get_address()
    print(f"minter: {address}")

    global_state = get_app_global_state(client, app_id)
    local_state = get_app_local_state(client, app_id, minter)
    balances = get_balances(client, address)

    mint_price = global_state[b"mp"]
    ally_reward_rate = global_state[b"rr"]
    previous_allys = 0

    if "allys" in local_state.keys():
        previous_allys = local_state[b"allys"]

    previous_algo  = balances[0]
    previous_walgo = 0
    transaction_count = 4

    if walgo_id in balances.keys():
        previous_walgo = balances[walgo_id]
        transaction_count = 3

    amount = 1_000_000

    mint_walgo(client, minter, app_id, walgo_id, amount)

    local_state = get_app_local_state(client, app_id, minter)
    balances = get_balances(client, address)

    current_allys = local_state[b"allys"]
    current_algo  = balances[0]
    current_walgo = balances[walgo_id]

    expect_minted_walgo = (amount * mint_price) / PRECISION

    assert current_walgo == previous_walgo + expect_minted_walgo 
    assert current_algo == previous_algo - amount - FEE * transaction_count

