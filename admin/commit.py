"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: set new values to global state before committing
How: `python admin/commit.py 3_000_000 1_003_000 950_000 10`
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Invalid argument counts!")
        exit(0)
    
    commit_amount = int(sys.argv[1])
    mint_price = int(sys.argv[2])
    redeem_price = int(sys.argv[3])
    fee_percentage = int(sys.argv[4])

    env = Env()
    params = env.client.suggested_params()
    params.fee = 2000

    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=params,
        index=env.pool_app_id,
        app_args=["commit", commit_amount, mint_price, redeem_price, fee_percentage],
        accounts=[env.governance],
        foreign_assets=[env.walgo_asa_id],
    )
    process_txn(env, txn)
