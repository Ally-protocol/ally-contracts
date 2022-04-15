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
    ally_address = get_application_address(env.ally_app_id)
    params = env.client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=params,
        index=env.pool_app_id,
        app_args=["claim_fee"],
        accounts=[ally_address],
        foreign_assets=[env.walgo_asa_id],
    )
    process_txn(env, txn)
