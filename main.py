# encoding: utf-8

import os

from endpoints import get_balance, get_utxos, get_blocks, get_blockdag, get_circulating_supply, get_kaspad_info, \
    get_network
from endpoints.get_blockreward import get_blockreward
from endpoints.get_hashrate import get_hashrate
from endpoints.get_marketcap import get_marketcap

print(
    f"Loaded: {get_balance}, {get_utxos}, {get_blocks}, {get_blockdag}, {get_circulating_supply}, "
    f"{get_kaspad_info}, {get_network}, {get_marketcap}, {get_hashrate}, {get_blockreward}")

from server import app

if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn

        uvicorn.run(app)