"""
Purpose: assign a new governor account
Actor: The current contract governor (admin)
When: changing the governor
Examples:
- python admin/set_governor.py pool AAA...YYY
- python admin/set_governor.py ally AAA...YYY
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    env = Env()

    if sys.argv[1] == "ally":
        app_id = env.ally_app_id
    
    if sys.argv[1] == "pool":
        app_id = env.pool_app_id
    
    governor = sys.argv[2]

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=app_id,
        app_args=["set_governor"],
        accounts=[governor]
    )
    process_txn(env, txn)
