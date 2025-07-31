import pytest

from openpipe.client import AsyncOpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)


@pytest.mark.asyncio
async def test_lists_models():
    """Test listing models and verifying model properties."""
    client = AsyncOpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = (await client.list_models()).data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None
