# encoding: utf-8
import asyncio
import os

import sockets
from endpoints import get_balance, get_utxos, get_blocks, get_blockdag, get_circulating_supply, get_kaspad_info, \
    get_network
from endpoints.get_blockreward import get_blockreward
from endpoints.get_hashrate import get_hashrate
from endpoints.get_marketcap import get_marketcap
from sockets.blockdag import periodical_blockdag
from sockets.blocks import config
from sockets.coinsupply import periodic_coin_supply

print(
    f"Loaded: {get_balance}, {get_utxos}, {get_blocks}, {get_blockdag}, {get_circulating_supply}, "
    f"{get_kaspad_info}, {get_network}, {get_marketcap}, {get_hashrate}, {get_blockreward}, {sockets.join_room}"
    f"{periodic_coin_supply} {periodical_blockdag}")

from server import app

# find kaspad before staring webserver
asyncio.run(get_network.get_network())
config()

if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn

        uvicorn.run(app)
