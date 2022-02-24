import os
import dotenv

from ally.account import Account
from ally.operations.user import mint_walgo
from ally.utils import get_algod_client, get_app_global_state, get_app_local_state, get_balances

PRECISION = 1_000_000_000
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
    previous_allys = local_state[b"allys"]
    previous_algo  = balances[0]
    previous_walgo = 0
    if walgo_id in balances.keys():
        previous_walgo = balances[walgo_id]

    amount = 1_000_000

    mint_walgo(client, minter, app_id, walgo_id, amount)

    local_state = get_app_local_state(client, app_id, minter)
    balances = get_balances(client, address)

    current_allys = local_state[b"allys"]
    current_algo  = balances[0]
    current_walgo = balances[walgo_id]


    assert current_allys - previous_allys == int((amount * ally_reward_rate)/PRECISION)

    # not working when changing mint_price
    # using another mint_price changes the result -300050 # TODO why are there 0.3 more walgos?
    assert current_walgo - previous_walgo == amount

    # not working when changing mint_price
    # using another mint_price changes the result +297050 # TODO why are there 0.29 less algos?
    assert previous_algo - current_algo - (amount * mint_price)/PRECISION <= FEE*4 #why 3 transactions?
