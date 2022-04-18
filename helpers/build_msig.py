"""
Purpose: get a multisig address
"""

import sys
sys.path.insert(0, '')
from algosdk.future import transaction

govs = [
    "4ZE4ER3UTCGHTL7XOONPSGRMMKAA6OBKBOYGEPNPJMUUBMAITTRMKJP74A",
    "OMP4WNBMJPXBTEBXJPYSFIUIUAQ2V63PSV36JOELQQRRMRGKT37ETNNOQA",
    "2S7FKSWTZTZRNCRTMCEML5NIRZCOUWFR54WFD7R2NRC6POTCE2W7DSLF5I"
]

threshold = 2
sigversion = 1

msig = transaction.Multisig(sigversion, threshold, govs)
address = msig.address()

print(address)
