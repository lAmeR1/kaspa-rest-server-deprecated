from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_marketcap

@pytest.mark.asyncio
async def test_get_marketcap_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/marketcap")
