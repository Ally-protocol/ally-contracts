"""
Purpose: creates 5 accounts for: Governors, Minter and Funder.
Mnemonics returned by this file should be copied to the .env file
These only work for the local sandbox.
Testnet accounts should be created manually in AlgoSigner or MyAlgoWallet.
"""

import os
import dotenv

from ally.utils import get_algod_client, get_kmd_client, get_balances, get_temporary_account

if __name__ == '__main__':
    dotenv.load_dotenv(".env")

    client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))    
    kmd = get_kmd_client(os.environ.get("KMD_ADDRESS"), os.environ.get("KMD_TOKEN"))

    signers = ["Governor 1", "Governor 2", "Governor 3", "Funder", "Minter"]

    for signer in signers:
        account = get_temporary_account(client, kmd)
        print(signer, " ------------------------------------------------ ")
        print(account.get_address())
        print(get_balances(client, account.get_address()))
        print(account.get_mnemonic())
