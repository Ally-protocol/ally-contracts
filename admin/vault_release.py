"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: sending all algo in vault to pool
How: `python admin/dev/vault_release.py 1`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.vault import release_vault
from ally.environment import Env

if __name__ == '__main__':
    env = Env()

    vault_number = int(sys.argv[1]) - 1
    vault_app_id = env.vault_IDs[vault_number]
    print(f"vault_app_id: {vault_app_id}")

    release_vault(vault_app_id)
    