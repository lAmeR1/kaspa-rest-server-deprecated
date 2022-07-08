# encoding: utf-8

import os

from endpoints import get_balance, get_utxos, get_blocks, get_blockdag, get_circulating_supply, get_kaspad_info, \
    get_network

print(
    f"Loaded: {get_balance}, {get_utxos}, {get_blocks}, {get_blockdag}, {get_circulating_supply}, {get_kaspad_info}, {get_network}")

from server import app

if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn

        uvicorn.run(app)