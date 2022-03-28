from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from ally.utils import send_transaction
from ally.account import Account

def set_multisig_governor(client: AlgodClient, sender: Account, app_id: int, msig: transaction.Multisig):
    print('sender address: ', sender.get_address())

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=[b"set_governor"],
        accounts=[msig.address()],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def toggle_redeem(client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["toggle_redeem"],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)
    

def set_mint_price(mint_price: int, client: AlgodClient, sender: Account, app_id: int, asset_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_mint_price", mint_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    send_transaction(client, sender, txn)


def set_redeem_price(redeem_price: int, client: AlgodClient, sender: Account, app_id: int, asset_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_redeem_price", redeem_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    send_transaction(client, sender, txn)


def set_ally_price(ally_price: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_price", ally_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def set_pool_id(pool_id: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_pool_id", pool_id.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def set_ally_reward_rate(ally_reward_rate: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_ally_reward_rate", ally_reward_rate.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def set_max_mint(max_mint: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_max_mint", max_mint.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def set_fee_percentage(fee_percentage: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_fee_percentage", fee_percentage.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)


def set_last_commit_price(last_commit_price: int, client: AlgodClient, sender: Account, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_last_commit_price", last_commit_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )
    send_transaction(client, sender, txn)


def claim_fee(client: AlgodClient, sender: Account, app_id: int, asset_id: int, ally_address: str):
    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["claim_fee"],
        on_complete=transaction.OnComplete.NoOpOC,
        accounts=[ally_address],
        foreign_assets=[asset_id]
    )
    
    send_transaction(client, sender, txn)