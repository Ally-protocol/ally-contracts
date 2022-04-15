from ally.environment import Env
from algosdk.future import transaction
from ally.process import process_txn

env = Env()

def toggle_redeem():
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["toggle_redeem"],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)
    

def set_mint_price(mint_price: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_mint_price", mint_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[env.walgo_asa_id]
    )
    process_txn(env, txn)


def set_redeem_price(redeem_price: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_redeem_price", redeem_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[env.walgo_asa_id]
    )
    process_txn(env, txn)


def set_ally_price(ally_price: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.ally_app_id,
        app_args=["set_price", ally_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)


def set_pool_id(pool_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.ally_app_id,
        app_args=["set_pool_id", pool_id.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)


def set_ally_reward_rate(ally_reward_rate: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_ally_reward_rate", ally_reward_rate.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)


def set_max_mint(max_mint: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_max_mint", max_mint.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)


def set_fee_percentage(fee_percentage: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_fee_percentage", fee_percentage.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)

def set_last_commit_price(last_commit_price: int):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["set_last_commit_price", last_commit_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    process_txn(env, txn)


def claim_fee(ally_address: str):
    txn = transaction.ApplicationCallTxn(
        sender=env.sender,
        sp=env.client.suggested_params(),
        index=env.pool_app_id,
        app_args=["claim_fee"],
        on_complete=transaction.OnComplete.NoOpOC,
        accounts=[ally_address],
        foreign_assets=[env.walgo_asa_id]
    )
    process_txn(env, txn)