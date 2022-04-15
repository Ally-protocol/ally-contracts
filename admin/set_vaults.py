"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: set 12 vaults address to pool app
How: `python admin/set_vaults.py`
"""

import sys
sys.path.insert(0, '')

from ally.vault import set_vaults
from ally.environment import Env

if __name__ == '__main__':
    env = Env()

    vault_group1 = [env.vaults[0], env.vaults[1], env.vaults[2], env.vaults[3]]
    vault_group2 = [env.vaults[4], env.vaults[5], env.vaults[6], env.vaults[7]]
    vault_group3 = [env.vaults[8], env.vaults[9], env.vaults[10], env.vaults[11]]

    group1_arg = "vault_group1"
    group2_arg = "vault_group2"
    group3_arg = "vault_group3"

    set_vaults(vault_group1, group1_arg)
    set_vaults(vault_group2, group2_arg)
    set_vaults(vault_group3, group3_arg)