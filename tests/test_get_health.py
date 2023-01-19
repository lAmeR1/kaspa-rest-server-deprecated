from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_health

@pytest.mark.asyncio
async def test_get_health_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/health")
