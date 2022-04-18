"""
Purpose: destroy a contract - ally or pool
Actor: The current contract governor (admin)
Examples:
- python deploy/destroy.py ally
- python deploy/destroy.py pool
"""

import sys
sys.path.insert(0, '')

from algosdk.future import transaction
from ally.environment import Env
from ally.process import process_txn


if __name__ == '__main__':
    env = Env()

    if(sys.argv[1] == "pool"):
        app_id = env.pool_app_id

    if(sys.argv[1] == "ally"):
        app_id = env.ally_app_id

    txn = transaction.ApplicationDeleteTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=app_id
    )
    
    process_txn(env, txn)
