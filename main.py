# encoding: utf-8
import asyncio
import os
from asyncio import Task, InvalidStateError

from fastapi_utils.tasks import repeat_every
from starlette.responses import RedirectResponse

import sockets
from endpoints import get_balance, get_utxos, get_blocks, get_blockdag, get_circulating_supply, get_kaspad_info, \
    get_network
from endpoints.get_blockreward import get_blockreward
from endpoints.get_halving import get_halving
from endpoints.get_hashrate import get_hashrate
from endpoints.get_health import health_state
from endpoints.get_marketcap import get_marketcap
from sockets import blocks
from sockets.blockdag import periodical_blockdag
from sockets.coinsupply import periodic_coin_supply

print(
    f"Loaded: {get_balance}, {get_utxos}, {get_blocks}, {get_blockdag}, {get_circulating_supply}, "
    f"{get_kaspad_info}, {get_network}, {get_marketcap}, {get_hashrate}, {get_blockreward}, {sockets.join_room}"
    f"{periodic_coin_supply} {periodical_blockdag} {get_halving} {health_state}")

from server import app, kaspad_client


BLOCKS_TASK = None  # type: Task


@app.on_event("startup")
async def startup():
    global BLOCKS_TASK
    # find kaspad before staring webserver
    await kaspad_client.initialize_all()
    BLOCKS_TASK = asyncio.create_task(blocks.config())


@app.on_event("startup")
@repeat_every(seconds=5)
async def watchdog():
    global BLOCKS_TASK

    try:
        exception = BLOCKS_TASK.exception()
    except InvalidStateError:
        pass
    else:
        print(f"Watch found an error! {exception}\n"
              f"Reinitialize kaspads and start task again")
        await kaspad_client.initialize_all()
        BLOCKS_TASK = asyncio.create_task(blocks.config())


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn
        uvicorn.run(app)
