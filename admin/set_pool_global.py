"""
Purpose: manipulate global integer variables in the pool contract
Actor: The current contract governor (admin)
Usage:
- python admin/set_pool_global.py max_mint 10_000_000
- python admin/set_pool_global.py last_commit_price 10_000_000
- python admin/set_pool_global.py fee_percentage 10
- python admin/set_pool_global.py ally_reward_rate 1_020_000
- python admin/set_pool_global.py mint_price 1_020_000
- python admin/set_pool_global.py redeem_price 995_000
"""

import sys
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction

if __name__ == '__main__':
    app_call = "set_" + sys.argv[1]
    value = int(sys.argv[2]).to_bytes(8, 'big')

    env = Env()
    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=[app_call, value],
        foreign_assets=[env.walgo_asa_id]
    )
    process_txn(env, txn)

    