import random
import json
from typing import List
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk import encoding

from ally.utils import wait_for_transaction
from ally.account import Account

def set_governor(client: AlgodClient, sender: Account, app_id: int, governors: List[Account], version: int, multisig_threshold: int):
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

    signed_call_txn = txn.sign(sender.get_private_key())
    tx_id = client.send_raw_transaction(encoding.msgpack_encode(signed_call_txn))

    wait_for_transaction(client, tx_id)


def toggle_redeem(client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["toggle_redeem"],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)
    

def set_mint_price(mint_price: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int, asset_id: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

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

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def set_redeem_price(redeem_price: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int, asset_id: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

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

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def set_ally_price(ally_price: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_price", ally_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def set_pool_id(pool_id: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_pool_id", pool_id.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)


def set_ally_reward_rate(ally_reward_rate: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(
        version, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_ally_reward_rate", ally_reward_rate.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)


def set_max_mint(max_mint: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(version, multisig_threshold, [governor.get_address() for governor in governors])

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_max_mint", max_mint.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def set_fee_percentage(fee_percentage: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(version, multisig_threshold, [governor.get_address() for governor in governors])

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_fee_percentage", fee_percentage.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)


def set_last_commit_price(last_commit_price: int, client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int):
    msig = transaction.Multisig(version, multisig_threshold, [governor.get_address() for governor in governors])

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["set_last_commit_price", last_commit_price.to_bytes(8, 'big')],
        on_complete=transaction.OnComplete.NoOpOC
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)



def claim_fee(client: AlgodClient, governors: List[Account], app_id: int, version: int, multisig_threshold: int, asset_id: int, ally_address: str):
    msig = transaction.Multisig(version, multisig_threshold, [governor.get_address() for governor in governors])

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["claim_fee"],
        on_complete=transaction.OnComplete.NoOpOC,
        accounts=[ally_address],
        foreign_assets=[asset_id]
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)


def vote(client: AlgodClient, governors: List[Account], app_id: int, multisig_threshold: int, governance: str):
    msig = transaction.Multisig(
        1, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

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

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)

def commit(commit_amount: int, client: AlgodClient, governors: List[Account], app_id: int, multisig_threshold: int, governance: str, asset_id: int):
    msig = transaction.Multisig(
        1, multisig_threshold,
        [governor.get_address() for governor in governors]
    )

    txn = transaction.ApplicationCallTxn(
        sender=msig.address(),
        sp=client.suggested_params(),
        index=app_id,
        app_args=["commit", "af/gov1-" + json.dumps({"com": commit_amount}), commit_amount],
        accounts=[governance],
        on_complete=transaction.OnComplete.NoOpOC,
        foreign_assets=[asset_id]
    )

    mtx = transaction.MultisigTransaction(txn, msig)

    print(f"Sender: {msig.address()}")

    idxs = random.sample(range(0, len(governors)), multisig_threshold)
    for idx in idxs:
        mtx.sign(governors[idx].get_private_key())

    tx_id = client.send_raw_transaction(encoding.msgpack_encode(mtx))

    wait_for_transaction(client, tx_id)