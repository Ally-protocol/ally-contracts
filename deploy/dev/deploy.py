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

from ally.operations.dev.deploy import bootstrap, create
from ally.utils import get_algod_client, get_app_global_state, get_balances, wait_for_transaction
from ally.account import Account


if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    if(len(sys.argv) < 2):
        print("available contracts: [pool | ally | vault]")
        exit(0)
    else:
        contract = sys.argv[1]


    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))
    funder = Account.from_mnemonic(os.environ.get("FUNDER_MNEMONIC"))
    app_id = create(contract, client, funder)

    print(f"APP ID: {app_id}")
    print(f"APP ADDRESS: {get_application_address(app_id)}")

    if ((get_balances(client, get_application_address(app_id))[0] < 300_000) and (contract != "vault")):
        pay_txn = transaction.PaymentTxn(
            sender=funder.get_address(),
            sp=client.suggested_params(),
            receiver=get_application_address(app_id),
            amt=1_001_000
        )
        signed_pay_txn = pay_txn.sign(funder.get_private_key())
        client.send_transaction(signed_pay_txn)
        wait_for_transaction(client, pay_txn.get_txid())
    
    if contract != "vault":
        bootstrap(client, funder, app_id)    
        state = get_app_global_state(client, app_id)
        print("Global State: ", state)
