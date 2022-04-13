"""
Purpose: manipulate the maximum mint amount per transaction
Actor: The current contract governor (admin)
When: setting claiming the pool fee
How: `python admin/claim_fee.py`
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction
from algosdk.logic import get_application_address

if __name__ == '__main__':
    env = Env()

    address_to = sys.argv[1]
    amount = int(sys.argv[2]).to_bytes(8, 'big')

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["flush", amount],
        accounts=[address_to],
    )
    process_txn(env, txn)
