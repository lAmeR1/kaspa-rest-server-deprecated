# encoding: utf-8
import time

import aiohttp
from aiocache import cached

FLOOD_DETECTED = False

@cached(ttl=120)
async def get_kas_price():
    global FLOOD_DETECTED
    if not FLOOD_DETECTED or time.time() - FLOOD_DETECTED > 300:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coingecko.com/api/v3/simple/price",
                                   params={"ids": "kaspa",
                                           "vs_currencies": "usd"},
                                   timeout=5) as resp:
                if resp.status == 200:
                    FLOOD_DETECTED = False
                    return (await resp.json())["kaspa"]["usd"]
                elif resp.status == 429:
                    FLOOD_DETECTED = time.time()
                    raise Exception("Rate limit exceeded.")
                else:
                    raise Exception("Did not retrieve the price.")


@cached(ttl=60)
async def get_kas_market_data():
    global FLOOD_DETECTED
    if not FLOOD_DETECTED or time.time() - FLOOD_DETECTED > 300:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coingecko.com/api/v3/coins/kaspa", timeout=5) as resp:
                if resp.status == 200:
                    FLOOD_DETECTED = False
                    return (await resp.json())["market_data"]
                elif resp.status == 429:
                    FLOOD_DETECTED = time.time()
                    raise Exception("Rate limit exceeded.")
                else:
                    raise Exception("Did not retrieve the market data.")
