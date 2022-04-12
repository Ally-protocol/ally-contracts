"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: committing to Algorand governance
How: `python admin/live/commit.py 3_000_000 1_003_000 950_000 10`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from algosdk import encoding
from ally.account import Account
from ally.operations.dev.admin import set_vaults
from ally.utils import get_algod_client, get_app_global_state, get_app_local_state, get_balances
from algosdk.future import transaction

if __name__ == '__main__':
    dotenv.load_dotenv('.env')

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    app_id = int(os.environ.get("POOL_APP_ID"))
    vault_id = int(os.environ.get("VAULT1_ID"))

    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    
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

    vault_group1 = [vault1, vault2, vault3, vault4]
    vault_group2 = [vault5, vault6, vault7, vault8]
    vault_group3 = [vault9, vault10, vault11, vault12]

    group1_arg = "vault_group1"
    group2_arg = "vault_group2"
    group3_arg = "vault_group3"

    set_vaults(client, funder, vault_group1, app_id, group1_arg)
    set_vaults(client, funder, vault_group2, app_id, group2_arg)
    set_vaults(client, funder, vault_group3, app_id, group3_arg)