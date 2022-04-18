"""
Purpose: send ALLY tokens to certain address
Actor: The current contract governor
Example: `ENV=testnet python admin/distribute_all.py AAA...HHH 1_000_000`
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    address_to = sys.argv[1]
    amount = int(sys.argv[2]).to_bytes(8, 'big')

    env = Env()
    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.ally_app_id,
        app_args=["distribute", amount],
        accounts=[address_to],
        foreign_assets=[env.ally_asa_id],
    )
    process_txn(env, txn)
