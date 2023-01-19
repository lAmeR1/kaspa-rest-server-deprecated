from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_transactions

test_transaction_id = "cb9d303dfe906d2127da5a94881af2d324398dd286b272a3b91be446d16060a9"

# TODO: Apply limiter to transactions/id
# @pytest.mark.asyncio
# async def test_get_transaction_rate_limit():
#     await kaspad_client.initialize_all()

#     await validate_rate_limit(f"/transactions/{test_transaction_id}?inputs=false&outputs=false")

# TODO: Apply limiter to transactions/search
