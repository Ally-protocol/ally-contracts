"""
Purpose: make a code upgrate in ally or pool contract
Actor: The current contract governor (admin)
Examples:
- python deploy/update.py ally
- python deploy/update.py pool
"""

import sys
sys.path.insert(0, '')

from base64 import b64decode
from algosdk.future import transaction
from ally.environment import Env
from ally.process import process_txn
from ally.contracts.pool import pool_approval_src, pool_clear_src
from ally.contracts.ally import ally_approval_src, ally_clear_src

if __name__ == '__main__':
    env = Env()

    if(sys.argv[1] == "pool"):
        app_result = env.client.compile(pool_approval_src())
        clear_result = env.client.compile(pool_clear_src())
        app_id = env.pool_app_id

    if(sys.argv[1] == "ally"):
        app_result = env.client.compile(ally_approval_src())
        clear_result = env.client.compile(ally_clear_src())
        app_id = env.ally_app_id

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])

    txn = transaction.ApplicationUpdateTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=app_id,
        approval_program=app_bytes,
        clear_program=clear_bytes
    )
    
    process_txn(env, txn)
