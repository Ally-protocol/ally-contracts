"""
Purpose: manipulate vote action
Actor: The current contract governor (admin)
When: vote to Algorand governance 
How: `python admin/vote.py`
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    key = sys.argv[1]
    value = sys.argv[2]
    vote_msg = 'af/gov1:j{' + key + ': " + value + "}'

    env = Env()
    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["vote", vote_msg],
        accounts=[env.governance],
    )
    process_txn(env, txn)
