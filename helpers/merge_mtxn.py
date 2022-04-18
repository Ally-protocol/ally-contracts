"""
Purpose: merge unsigned transaction files
How: `python admin/merge_mtxn.py`
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from ally.environment import Env
from algosdk.future import transaction
from ally.utils import wait_for_transaction


if __name__ == '__main__':
    env = Env()

    unsigned_tx = transaction.retrieve_from_file(env.output + "/unsigned.mtx")
    mtx = unsigned_tx[0]

    sign1_tx = transaction.retrieve_from_file(env.output + "/governor1.signed.txn")
    sign2_tx = transaction.retrieve_from_file(env.output + "/governor2.signed.txn")
    sign3_tx = transaction.retrieve_from_file(env.output + "/governor3.signed.txn")

    signed_mtx = mtx.merge([sign1_tx[0], sign2_tx[0], sign3_tx[0]])
    tx_id = env.client.send_transaction(signed_mtx)

    wait_for_transaction(client, tx_id)
