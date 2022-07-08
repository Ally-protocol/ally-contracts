"""
Deploys pool.py or ally.py contracts
Deployment retuns an app_id that should be copied to the corresponding .env file
"""

import sys
sys.path.insert(0, '')

from base64 import b64decode
from algosdk.logic import get_application_address
from algosdk.future import transaction
from ally.environment import Env
from ally.process import process_txn
from ally.contracts.pool import pool_approval_src, pool_clear_src
from ally.contracts.ally import ally_approval_src, ally_clear_src
from ally.contracts.vault import vault_approval_src, vault_clear_src


if __name__ == '__main__':
    env = Env()

    if(sys.argv[1] == "pool"):
        app_result = env.client.compile(pool_approval_src())
        clear_result = env.client.compile(pool_clear_src())

    if(sys.argv[1] == "ally"):
        app_result = env.client.compile(ally_approval_src())
        clear_result = env.client.compile(ally_clear_src())
    
    if(sys.argv[1] == "vault"):
        app_result = env.client.compile(vault_approval_src())
        clear_result = env.client.compile(vault_clear_src())

    app_bytes = b64decode(app_result["result"])
    clear_bytes = b64decode(clear_result["result"])

    global_schema = transaction.StateSchema(num_uints=32, num_byte_slices=32)
    local_schema = transaction.StateSchema(num_uints=8, num_byte_slices=8)

    if sys.argv[1] != "vault":
        txn = transaction.ApplicationCreateTxn(
            on_complete=transaction.OnComplete.NoOpOC,
            sender=env.sender,
            sp=env.client.suggested_params(),
            approval_program=app_bytes,
            clear_program=clear_bytes,
            global_schema=global_schema,
            local_schema=local_schema,
        )
    else:
        txn = transaction.ApplicationCreateTxn(
            sender=env.sender,
            sp=env.client.suggested_params(),
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=[env.walgo_asa_id],
            accounts=[env.pool_app_address],
            approval_program=app_bytes,
            clear_program=clear_bytes,
            global_schema=global_schema,
            local_schema=local_schema,
        )

    response = process_txn(env, txn)
    
    if env.autosign:
        app_id = response.application_index
        assert app_id is not None and app_id > 0
        
        app_address = get_application_address(app_id)
        print(f"APP ID: {app_id}")
        print(f"APP ADDRESS: {app_address}")

        pay_txn = transaction.PaymentTxn(
            sender=env.sender,
            sp=env.client.suggested_params(),
            receiver=app_address,
            amt=1_001_000
        )
        process_txn(env, pay_txn)
