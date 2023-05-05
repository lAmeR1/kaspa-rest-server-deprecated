# encoding: utf-8
import logging
import os

from starlette.responses import RedirectResponse

from dbsession import create_all
from endpoints import get_balance, get_utxos, get_blocks, get_blockdag, get_circulating_supply, get_kaspad_info, \
    get_network, get_price
from endpoints.get_address_transactions import get_transactions_for_address
from endpoints.get_blockreward import get_blockreward
from endpoints.get_halving import get_halving
from endpoints.get_hashrate import get_hashrate
from endpoints.get_health import health_state
from endpoints.get_marketcap import get_marketcap
from endpoints.get_transactions import get_transaction
from endpoints.get_virtual_chain_blue_score import get_virtual_selected_parent_blue_score
from endpoints.kaspad_requests.submit_transaction_request import submit_a_new_transaction
from helper import get_kas_market_data
from server import app, kaspad_client

IS_SQL_DB_CONFIGURED = os.getenv("SQL_URI") is not None

print(
    f"Loaded: {get_balance}, {get_utxos}, {get_blocks}, {get_blockdag}, {get_circulating_supply}, "
    f"{get_kaspad_info}, {get_network}, {get_marketcap}, {get_hashrate}, {get_blockreward}"
    f"{get_halving} {health_state} {get_transaction}"
    f"{get_virtual_selected_parent_blue_score} {get_transactions_for_address}"
    f"{submit_a_new_transaction} {get_price}")

if os.getenv('VSPC_REQUEST') == 'true':
    from endpoints.get_vspc import get_virtual_selected_parent_chain_from_block

    print(get_virtual_selected_parent_chain_from_block)


@app.on_event("startup")
async def startup():
    # create db if needed
    if IS_SQL_DB_CONFIGURED:
        await create_all(drop=False)
    # get kaspad
    await get_kas_market_data()

    # find kaspad before staring webserver
    await kaspad_client.initialize_all()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


logging.basicConfig(format="%(asctime)s::%(levelname)s::%(name)s::%(message)s",
                    level=logging.DEBUG if os.getenv("DEBUG", False) else logging.INFO,
                    handlers=[logging.StreamHandler()])

if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn

        uvicorn.run(app)
