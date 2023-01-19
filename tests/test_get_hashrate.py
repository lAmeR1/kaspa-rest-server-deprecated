from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_hashrate

@pytest.mark.asyncio
async def test_get_hashrate_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/hashrate")

# @pytest.mark.asyncio
# async def test_get_hashrate_max_rate_limit():
#     await kaspad_client.initialize_all()

#     await validate_rate_limit("/info/hashrate/max")
