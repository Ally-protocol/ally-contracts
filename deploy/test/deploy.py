"""
Deploys pool.py or ally.py contracts
Deployment retuns an app_id that should be copied to the .env file
Deployment is set to be done using a multisignature account composed by 3 governors
After that, all governor (admin) actions in the 'admin' folder must be done by the same multisignature account
"""

import sys
sys.path.insert(0, '')

import os
import dotenv

from algosdk.logic import get_application_address
from algosdk.future import transaction

from ally.operations.test.deploy import bootstrap, create
from ally.utils import get_algod_client, get_app_global_state, get_balances, wait_for_transaction
from ally.account import Account


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    if(len(sys.argv) < 2):
        print("available contracts: [pool | ally]")
        exit(0)
    else:
        contract = sys.argv[1]


    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

    governor1 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR1_MNEMONIC"))
    governor2 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR2_MNEMONIC"))
    governor3 = Account.from_mnemonic(os.environ.get("TEST_GOVERNOR3_MNEMONIC"))
    threshold = int(os.environ.get("MULTISIG_THRESHOLD"))
    governors = [governor1, governor2, governor3]
    
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    
    msig = transaction.Multisig(1, threshold, [governor.get_address() for governor in governors])
    
    if get_balances(client, msig.address())[0] < 6_000_000:
        pay_txn = transaction.PaymentTxn(
            sender=funder.get_address(),
            sp=client.suggested_params(),
            receiver=msig.address(),
            amt=6_000_000
        )
        signed_pay_txn = pay_txn.sign(funder.get_private_key())
        client.send_transaction(signed_pay_txn)
        wait_for_transaction(client, pay_txn.get_txid())

    print(f"DEPLOYER: {msig.address()}")

    app_id = create(contract, client, governors, threshold)

    print(f"APP ID: {app_id}")
    print(f"APP ADDRESS: {get_application_address(app_id)}")

    if get_balances(client, get_application_address(app_id))[0] < 300_000:
        pay_txn = transaction.PaymentTxn(
            sender=funder.get_address(),
            sp=client.suggested_params(),
            receiver=get_application_address(app_id),
            #amt=202_000
            amt=1_001_000
        )
        signed_pay_txn = pay_txn.sign(funder.get_private_key())
        client.send_transaction(signed_pay_txn)
        wait_for_transaction(client, pay_txn.get_txid())
    
    bootstrap(client, governors, threshold, app_id)
    
    state = get_app_global_state(client, app_id)
    
    print("Global State: ", state)