"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: distributing algo to Algorand governance
How: `python admin/distribute.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.vault import distribute_vault
from ally.environment import Env
from ally.utils import get_balances

VAULT_GROUP_COUNT = 3
ONE_ALGO = 1_000_000

if __name__ == '__main__':
    env = Env()

    vault_group1 = [env.vaults[0], env.vaults[1], env.vaults[2], env.vaults[3]]
    vault_group2 = [env.vaults[4], env.vaults[5], env.vaults[6], env.vaults[7]]
    vault_group3 = [env.vaults[8], env.vaults[9], env.vaults[10], env.vaults[11]]

    group1_arg = "vault_group1"
    group2_arg = "vault_group2"
    group3_arg = "vault_group3"

    balances = get_balances(env.client, env.pool_app_address)
    commit_amount = int(balances[0] / VAULT_GROUP_COUNT) - ONE_ALGO

    distribute_vault(commit_amount, vault_group1, group1_arg)
    distribute_vault(commit_amount, vault_group2, group2_arg)
    distribute_vault(commit_amount, vault_group3, group3_arg)
    