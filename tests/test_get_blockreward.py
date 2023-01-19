from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_blockreward

base_url="http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_get_blockreward_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/blockreward")
    