"""
Purpose: initialize a contract after its creation
Actor: The current contract governor (admin)
Examples:
- python deploy/bootstrap.py ally
- python deploy/bootstrap.py pool
"""

import sys
sys.path.insert(0, '')

from algosdk.future import transaction
from ally.environment import Env
from ally.process import process_txn
from ally.utils import get_app_global_state

if __name__ == '__main__':
    env = Env()

    if(sys.argv[1] == "pool"):
        app_id = env.pool_app_id

    if(sys.argv[1] == "ally"):
        app_id = env.ally_app_id

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=app_id,
        app_args=["bootstrap"],
    )

    process_txn(env, txn)

    print("Global State: ", get_app_global_state(env.client, app_id))
