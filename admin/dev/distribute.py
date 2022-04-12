"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: distributing algo to Algorand governance
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from algosdk import encoding
from ally.account import Account
from ally.operations.dev.admin import distribute_vault
from ally.utils import get_algod_client, get_balances
from algosdk.future import transaction

VAULT_GROUP_COUNT = 3
ONE_ALGO = 1_000_000

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    walgo_id = int(os.environ.get("WALGO_ID"))
    pool_address = os.environ.get("POOL_APP_ADDRESS")
    
    vault1 = os.environ.get("VAULT1")
    vault2 = os.environ.get("VAULT2")
    vault3 = os.environ.get("VAULT3")
    vault4 = os.environ.get("VAULT4")
    vault5 = os.environ.get("VAULT5")
    vault6 = os.environ.get("VAULT6")
    vault7 = os.environ.get("VAULT7")
    vault8 = os.environ.get("VAULT8")
    vault9 = os.environ.get("VAULT9")
    vault10 = os.environ.get("VAULT10")
    vault11 = os.environ.get("VAULT11")
    vault12 = os.environ.get("VAULT12")

    vault1 = [vault1, vault2, vault3, vault4]
    vault2 = [vault5, vault6, vault7, vault8]
    vault3 = [vault9, vault10, vault11, vault12]

    group1_arg = "vault_group1"
    group2_arg = "vault_group2"
    group3_arg = "vault_group3"

    balances = get_balances(client, pool_address)
    commit_amount = int(balances[0] / VAULT_GROUP_COUNT) - ONE_ALGO

    distribute_vault(commit_amount, client, vault1, group1_arg, funder, app_id, walgo_id)
    distribute_vault(commit_amount, client, vault2, group2_arg, funder, app_id, walgo_id)
    distribute_vault(commit_amount, client, vault3, group3_arg, funder, app_id, walgo_id)
    