"""
Purpose: manipulate commit action for Algorand governance
Actor: The current contract governor (admin)
When: committing algo in vault to Algorand governance
How: `python admin/vault_commit.py 1 3_000_000 950_000`
"""

import sys
import json
sys.path.insert(0, '')

from ally.environment import Env
from ally.process import process_txn
from algosdk.future import transaction
from ally.utils import wait_for_transaction

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Invalid argument counts!")
        exit(0)

    env = Env()

    vault_number = int(sys.argv[1])
    commit_amount = int(sys.argv[2])
    new_redeem_price = int(sys.argv[3])

    vault_id = env.vault_IDs[vault_number - 1]
    print(f"vault_id: {vault_id}")

    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=vault_id,
        app_args=["commit", "af/gov1:j" + json.dumps({"com": commit_amount}), commit_amount, new_redeem_price],
        accounts=[env.governance],
        foreign_assets=[env.walgo_asa_id],
        on_complete=transaction.OnComplete.NoOpOC,
    )
    process_txn(env,txn)
