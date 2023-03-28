# encoding: utf-8
import aiohttp
from aiocache import cached


@cached(ttl=120)
async def get_kas_price():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coingecko.com/api/v3/simple/price",
                               params={"ids": "kaspa",
                                       "vs_currencies": "usd"},
                               timeout=5) as resp:
            if resp.status == 200:
                return (await resp.json())["kaspa"]["usd"]
            else:
                raise Exception("Did not retrieve the price.")


@cached(ttl=60)
async def get_kas_market_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coingecko.com/api/v3/coins/kaspa", timeout=5) as resp:
            if resp.status == 200:
                return (await resp.json())["market_data"]
            else:
                raise Exception("Did not retrieve the market data.")
