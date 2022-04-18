import json

from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from typing import List
from ally.utils import send_transaction, wait_for_transaction
from ally.account import Account
from ally.environment import Env
from ally.process import process_txn

env = Env()

def set_vaults(vaults: List[str], group_arg: str):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_vaults", group_arg],
        accounts=vaults,
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)

def set_governor(governor: str, vault_id: int):
    txn = transaction.ApplicationCallTxn(
        on_complete=transaction.OnComplete.NoOpOC,
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=vault_id,
        app_args=["set_governor"],
        accounts=[governor]
    )
    process_txn(env, txn)

def distribute_vault(commit_amount: int, vaults: List[str], group_arg: str):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["distribute_algo", commit_amount, group_arg],
        accounts=vaults,
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[env.walgo_asa_id]
    )
    process_txn(env, txn)

def release_vault(app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=app_id,
        app_args=["release"],
        accounts=[env.pool_app_address],
        on_complete=transaction.OnComplete.NoOpOC,
    )
    process_txn(env, txn)