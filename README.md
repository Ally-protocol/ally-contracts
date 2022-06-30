# Ally for Algorand Governance

### Environment setup

- Install Docker and Docker-Compose.

- Set up python virtual environment.

```
python3 -m venv venv
source venv/bin/activate
```

- Install Dependencies
```
pip install -r requirements.txt
```

First, start an instance of sandbox (requires Docker):

```
./sandbox up
```

When finished, the sandbox can be stopped with: 

```
./sandbox down
```

Before running commands you have to create the .env file based on the .env.example

In order to get the MNEMONICS for 3 governors, 1 funder and 1 minter, run:

```
python setup.py
```

and fill the governors, minter and funder mnemonics from that command's output

this only works as a shortcut for the local sandbox, when using testnets or mainnet
you need to create accounts manually on AlgoSigner.

also the MULTISIG_THRESHOLD should be filled with a number equal or less than the amount of governors - currently 3

### Contract Deploy and update

- Deploy contract

```
python deploy/create.py pool
python deploy/create.py ally
```

The deployment returns an APP_ID that you have to insert in the .env file.
Insert them in POOL_APP_ID and ALLY_APP_ID correspondingly.

- Create token

```
python deploy/bootstrap.py pool
python deploy/bootstrap.py ally
```

These commands returns the WALGO_ID and ALLY_ID in the "pt" and "tk" key. Copy it to .env.

- Update contract

Ally supports time delay function to update contract.
There are 2 steps to update contract codes

1. Update request

```
python deploy/update_request.py pool
```

The updated smart contract Approval Program and Clear State Program are hashed using SHA256 and passed in as arguments and stored in global state when the update is requested. The timestamp of the request is also stored in global state.

2. Update execution

```
python deploy/update_execution.py pool
```

Contract code is updated only when the current timestamp is greater than the request timestamp plus the 7-day protection window (stored in global state in seconds).
And its Approval Program or Clear State Program, when hashed by the smart contract, match those that are stored in global state

### Admin Actions

- Set pool app id to ally contract

```
python admin/set_ally_global.py pool_id 
```

- Set ally token price

```
python admin/set_ally_global.py price 500_000
```

- Set values to global states of pool contract

```
python admin/set_pool_global.py max_mint 10_000_000
python admin/set_pool_global.py last_commit_price 10_000_000
python admin/set_pool_global.py fee_percentage 10
python admin/set_pool_global.py ally_reward_rate 1_020_000
python admin/set_pool_global.py mint_price 1_030_000
python admin/set_pool_global.py redeem_price 995_000
```

- Allow/Disable redeem

```
python admin/toggle_redeem.py
```

- Set governor

```
python admin/set_governor.py pool GTQX2L65LCZHB646F5QV5BY2SY3TTIKKST7JMXG5IQBXQGCWHFXPG62XQM
```

- Create vault

```
python deploy/create.py vault
```
This command returns app id and adddress that you have to insert it to env file.
We should run this command 12 times for creating 12 vaults.

- Set vaults to pool contract

```
python admin/set_vaults.py
```

- Set new values to global states of pool contract before committing

```
 python admin/commit.py 3_000_000 1_003_000 950_000 10                           
```

Here, 3_000_000 is commit amount, 1_003_000 is mint price, 950_000 is redeem price and 10 is fee percent

- Distribute all ALGO in pool contract into 12 vaults for Algrand goverance

```
python admin/distribute.py
```

- Return back ALGO in vault to pool contract

```
python admin/vault_release.py 1
```

Here 1 is vault number

### Run tests
```
pytest
```

Or

```
python -m pytest tests/  
```
