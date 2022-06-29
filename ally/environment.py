import sys
sys.path.insert(0, '')
import os
import dotenv
from algosdk.future import transaction
from ally.utils import get_algod_client
from .account import Account


class Env:
    def __init__(self):

        target = os.environ.get("ENV")
        if(target == None):
            dotenv.load_dotenv('.env')
        else:
            name = "./env/." + target
            dotenv.load_dotenv(name)

        self.client = get_algod_client(os.environ.get("ALGOD_URL"), os.environ.get("ALGOD_API_KEY"))

        self.output = os.environ.get("OUTPUT")
        self.governance = os.environ.get("GOVERNANCE")

        self.autosign = os.environ.get("AUTOSIGN") == 'true'
        self.multisig = os.environ.get("MULTISIG") == 'true'
        self.sigversion = int(os.environ.get("SIGVERSION"))
        self.threshold = int(os.environ.get("THRESHOLD"))

        self.signer = os.environ.get("SIGNER")
        self.gov1 = os.environ.get("GOVERNOR1")
        self.gov2 = os.environ.get("GOVERNOR2")
        self.gov3 = os.environ.get("GOVERNOR3")

        self.vaults = [
            os.environ.get("VAULT1"),
            os.environ.get("VAULT2"),
            os.environ.get("VAULT3"),
            os.environ.get("VAULT4"),
            os.environ.get("VAULT5"),
            os.environ.get("VAULT6"),
            os.environ.get("VAULT7"),
            os.environ.get("VAULT8"),
            os.environ.get("VAULT9"),
            os.environ.get("VAULT10"),
            os.environ.get("VAULT11"),
            os.environ.get("VAULT12")
        ]

        self.vault_IDs = [
            os.environ.get("VAULT1_ID"),
            os.environ.get("VAULT2_ID"),
            os.environ.get("VAULT3_ID"),
            os.environ.get("VAULT4_ID"),
            os.environ.get("VAULT5_ID"),
            os.environ.get("VAULT6_ID"),
            os.environ.get("VAULT7_ID"),
            os.environ.get("VAULT8_ID"),
            os.environ.get("VAULT9_ID"),
            os.environ.get("VAULT10_ID"),
            os.environ.get("VAULT11_ID"),
            os.environ.get("VAULT12_ID")
        ]

        if os.environ.get("POOL_APP_ID") != '':
            self.pool_app_id = int(os.environ.get("POOL_APP_ID"))
            self.pool_app_address = os.environ.get("POOL_APP_ADDRESS")
    
        if os.environ.get("ALLY_APP_ID") != '':
            self.ally_app_id = int(os.environ.get("ALLY_APP_ID"))
        
        if os.environ.get("WALGO_ASA_ID") != '':
            self.walgo_asa_id = int(os.environ.get("WALGO_ASA_ID"))

        if os.environ.get("ALLY_ASA_ID") != '':
            self.ally_asa_id = int(os.environ.get("ALLY_ASA_ID"))

        self.sender = self.signer
        self.signer_pk = Account.from_mnemonic(os.environ.get('SIGNER_MNEMONIC')).get_private_key()

        if self.multisig:
            self.govs = [self.gov1, self.gov2, self.gov3]
            self.msig = transaction.Multisig(self.sigversion, self.threshold, self.govs)
            self.sender = self.msig.address()

            if self.autosign:

                gov1_pk = Account.from_mnemonic(os.environ.get('GOVERNOR1_MNEMONIC')).get_private_key()
                gov2_pk = Account.from_mnemonic(os.environ.get('GOVERNOR2_MNEMONIC')).get_private_key()
                gov3_pk = Account.from_mnemonic(os.environ.get('GOVERNOR3_MNEMONIC')).get_private_key()
                self.gov_pks = [gov1_pk, gov2_pk, gov3_pk]

        if os.environ.get("MINTER_MNEMONIC") != '':
            self.minter = Account.from_mnemonic(os.environ.get("MINTER_MNEMONIC"))