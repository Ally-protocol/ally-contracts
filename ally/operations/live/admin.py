import os
import random
import json
from datetime import datetime
from typing import List
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address
from algosdk import encoding

from ally.utils import wait_for_transaction, send_transaction
from ally.account import Account

def set_governor(client: AlgodClient, sender: Account, app_id: int, msig: transaction.Multisig):
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
    save_mtx_file(mtx)

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

def toggle_redeem(client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["toggle_redeem"],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)
    
    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)
    

def set_mint_price(mint_price: int, client: AlgodClient, msig: transaction.Multisig, app_id: int, asset_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_mint_price", mint_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def set_redeem_price(redeem_price: int, client: AlgodClient, msig: transaction.Multisig, app_id: int, asset_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_redeem_price", redeem_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def set_ally_price(ally_price: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_price", ally_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def set_pool_id(pool_id: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_pool_id", pool_id.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def set_ally_reward_rate(ally_reward_rate: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_ally_reward_rate", ally_reward_rate.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)
    
    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def set_max_mint(max_mint: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_max_mint", max_mint.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)

def set_fee_percentage(fee_percentage: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_fee_percentage", fee_percentage.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)

def set_last_commit_price(last_commit_price: int, client: AlgodClient, msig: transaction.Multisig, app_id: int):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_last_commit_price", last_commit_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)


def claim_fee(client: AlgodClient, msig: transaction.Multisig, app_id: int, version: int, asset_id: int, ally_address: str):
    params = client.suggested_params()
    #params.fee = 5000

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=params,
        index=app_id,
        app_args=["claim_fee"],
        on_complete=transaction.OnComplete.NoOpOC,
        accounts=[ally_address],
        foreign_assets=[asset_id]
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)

def vote(client: AlgodClient, msig: transaction.Multisig, app_id: int, governance: str):
    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["vote", 'af/gov1:j[5: "a"]'],
        accounts=[governance],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)

def commit(commit_amount: int, client: AlgodClient, msig: transaction.Multisig, app_id: int, asset_id: int, governance: str, new_mint_price: int, new_redeem_price: int, new_fee_percent: int):
    params = client.suggested_params()
    #params.fee = 5000

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=params,
        index=app_id,
        app_args=["commit", "af/gov1:j" + json.dumps({"com": commit_amount}), commit_amount, new_mint_price, new_redeem_price, new_fee_percent],
        accounts=[governance],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id],
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")
    save_mtx_file(mtx)
    

def save_mtx_file(mtx: transaction.MultisigTransaction):
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, 'tx_files')

    filename = '/unsigned.mtx'

    transaction.write_to_file(
        [mtx], file_path + filename)

def merge_signed_transactions(client: AlgodClient, msig: transaction.Multisig):
    print(f"Sender: {msig.address()}")

    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, 'tx_files')

    unsigned_tx = transaction.retrieve_from_file(file_path + "/unsigned.mtx")
    mtx = unsigned_tx[0]

    sign1_tx = transaction.retrieve_from_file(file_path + "/governor1.signed.txn")
    sign2_tx = transaction.retrieve_from_file(file_path + "/governor2.signed.txn")
    sign3_tx = transaction.retrieve_from_file(file_path + "/governor3.signed.txn")

    signed_mtx = mtx.merge([sign1_tx[0], sign2_tx[0], sign3_tx[0]])
    tx_id = client.send_transaction(signed_mtx)

    wait_for_transaction(client, tx_id)