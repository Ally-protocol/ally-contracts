import random
import json

from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction

from typing import List
from ally.utils import send_transaction, wait_for_transaction
from ally.account import Account
from algosdk import encoding

def set_governor_M_to_1(client: AlgodClient, sender: Account, app_id: int, governors: List[Account], version: int, multisig_threshold: int):
    msig = transaction.Multisig(
        version, multisig_threshold, [governor.get_address() for governor in governors]
    )

    print('multisig address: ', msig.address())

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=[b"set_governor"],
        accounts=[sender.get_address()],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def set_governor_1_to_M(client: AlgodClient, sender: Account, app_id: int, msig: transaction.Multisig):
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

def set_vaults(client: AlgodClient, sender: Account, vaults: List[str], app_id: int, group_arg: str):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["set_vaults", group_arg],
        accounts=vaults,
        on_complete=transaction.OnComplete.NoOpOC
    )

    send_transaction(client, sender, txn)

def distribute_vault(commit_amount: int, client: AlgodClient, vaults: List[str], group_arg: str, sender: Account, app_id: int, asset_id: int):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["distribute_algo", commit_amount, group_arg],
        accounts=vaults,
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    send_transaction(client, sender, txn)

def commit(client: AlgodClient, sender: Account, app_id: int, new_mint_price: int, new_redeem_price: int, new_fee_percent: int):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["commit", new_mint_price, new_redeem_price, new_fee_percent],
        on_complete=transaction.OnComplete.NoOpOC,
    )

    send_transaction(client, sender, txn)

def commit_vault(commit_amount: int, client: AlgodClient, sender: Account, app_id: int, asset_id: int, governance: str, new_redeem_price: int):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["commit", "af/gov1:j" + json.dumps({"com": commit_amount}), commit_amount, new_redeem_price],
        accounts=[governance],
        foreign_assets=[asset_id],
        on_complete=transaction.OnComplete.NoOpOC,
    )

    send_transaction(client, sender, txn)

def vote_vault(client: AlgodClient, sender: Account, app_id: int, asset_id: int, governance: str):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["vote", 'af/gov1:j[5: "a"]'],
        accounts=[governance],
        foreign_assets=[asset_id],
        on_complete=transaction.OnComplete.NoOpOC,
    )

    send_transaction(client, sender, txn)

def release_vault(client: AlgodClient, sender: Account, pool_address: str, app_id: int):
    params = client.suggested_params()

    txn = transaction.ApplicationCallTxn(
        sender=sender.get_address(),
        sp=params,
        index=app_id,
        app_args=["release"],
        accounts=[pool_address],
        on_complete=transaction.OnComplete.NoOpOC,
    )

    send_transaction(client, sender, txn)