"""
Purpose: enable/disable wALGO token redemption
Actor: the current contract governor (admin)
When: the redeem period starts or ends
How: `python admin/toggle_redeem.py`
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    env = Env()
    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["toggle_redeem"],
    )
    process_txn(env, txn)
