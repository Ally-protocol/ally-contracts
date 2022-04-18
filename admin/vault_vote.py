"""
Purpose: manipulate vote action for Algorand governance
Actor: The current contract governor (admin)
When: voting to Algorand governance
How: `python admin/dev/vault_vote.py 1`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.environment import Env
from ally.utils import wait_for_transaction
from algosdk.future import transaction

if __name__ == '__main__':
    env = Env()

    vault_number = int(sys.argv[1])
    vault_id = env.vault_IDs[vault_number - 1]
    print(f"vault_id: {vault_id}")

    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=vault_id,
        app_args=["vote", 'af/gov1:j[5: "a"]'],
        accounts=[env.governance],
        foreign_assets=[env.walgo_asa_id],
        on_complete=transaction.OnComplete.NoOpOC,
    )

    transaction.assign_group_id([txn])

    signed_txn = txn.sign(env.signer_pk)
    tx_id = env.client.send_transactions([signed_txn])

    wait_for_transaction(env.client, tx_id)
    