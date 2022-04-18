"""
Purpose: assign a new governor account
Actor: The current contract governor (admin)
When: changing the governor
How: `python admin/set_governor.py AAAA...`
"""

import sys
sys.path.insert(0, '')

from ally.vault import set_governor
from ally.environment import Env

if __name__ == '__main__':
    env = Env()

    governor = sys.argv[1]

    for vault_id in env.vault_IDs:
        set_governor(governor, vault_id)

