"""
Purpose: manipulate global integer variables in the ally contract
Actor: The current contract governor (admin)
Usage:
- python admin/set_ally_global.py pool_id
- python admin/set_ally_global.py price 500_000
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    env = Env()
    app_call = "set_" + sys.argv[1]

    if app_call == 'set_pool_id':
        value = env.pool_app_id
    else:    
        value = int(sys.argv[2]).to_bytes(8, 'big')

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.ally_app_id,
        app_args=[app_call, value],
    )
    process_txn(env, txn)

    