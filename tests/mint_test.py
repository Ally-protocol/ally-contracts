import os
import dotenv

from ally.account import Account
from ally.operations import mint_walgo
from ally.utils import get_algod_client, get_app_global_state, get_balances

PRECISION = 1_000_000_000
FEE = 1000

dotenv.load_dotenv('.env')

client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
app_id = int(os.environ.get("APP_ID"))
walgo_id = int(os.environ.get("WALGO_ID"))
minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))


def test_mint():
    address = minter.get_address()
    print(f"minter: {address}")

    mint_price = get_app_global_state(client, app_id)[b"mp"]

    balances = get_balances(client, address)
    previous_algo  = balances[0]
    previous_walgo = 0
    if walgo_id in balances.keys():
        previous_walgo = balances[walgo_id]

    amount = 1_000_000

    mint_walgo(client, minter, app_id, walgo_id, amount)

    balances = get_balances(client, address)
    current_algo  = balances[0]
    current_walgo = balances[walgo_id]

    current_plus_paid = current_algo + (amount * mint_price)/PRECISION

    print(current_plus_paid - previous_algo)

    # not working when changing mint_price
    # using another mint_price changes the result -300050 # TODO why are there 0.3 more walgos?
    assert previous_walgo == current_walgo - amount
    
    # not working when changing mint_price
    # using another mint_price changes the result +297050 # TODO why are there 0.29 less algos?
    assert previous_algo - current_plus_paid <= FEE*3 #why 3 transactions?
    
