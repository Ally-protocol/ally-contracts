# Ally for Algorand Governance

- Install Docker and Docker-Compose.

- Environment setup

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

- Deploy contract and create pool token

```
python deploy/deploy.py pool
python deploy/deploy.py ally
```

The deployment returns an APP_ID that you have to insert in the .env file.
Insert them in POOL_APP_ID and ALLY_APP_ID correspondingly.
Each deploy returns the global state.
The pool deployment returns the WALGO_ID in the "pt" key. Copy it to .env.
The ally deployment returns the ALLY_ID in the "tk" key. Copy it to .env.

- Run tests
```
pytest
```

- Governor Actions (or admin actions)
```
python admin/mint_price --get | --set
python admin/set_governor
python admin/toggle_redeem
```
