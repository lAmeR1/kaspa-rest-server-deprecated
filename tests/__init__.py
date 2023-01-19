# encoding: utf-8

from httpx import AsyncClient

from server import app

import asyncio

base_url="http://127.0.0.1:8000"

async def validate_rate_limit(target_url: str, success_status_code=200, rate_limit=2, seconds_to_wait=1):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        # Do 1 request more than the limit
        responses = await asyncio.gather(*[ac.get(target_url) for _ in range (rate_limit + 1)])

        # All the requests within limit should return code 200
        for i in range(rate_limit):
            assert responses[i].status_code == success_status_code

        # The excess one should return 429
        assert responses[rate_limit].status_code == 429

        # Let the rate limit reset:
        await asyncio.sleep(seconds_to_wait)

        # New request should pass
        last_response = await ac.get(target_url)

        assert last_response.status_code == success_status_code