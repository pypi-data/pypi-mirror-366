import pytest
from openai import AsyncOpenAI

from openpipe.client import AsyncOpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)


@pytest.mark.asyncio
async def test_gets_fine_tuned_model_using_openpipe_client():
    """Test retrieving fine-tuned models using the OpenPipe client."""
    client = AsyncOpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = (await client.list_models()).data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None

    model = await client.get_model(model_slug=first_model.id)

    assert model.id is not None


@pytest.mark.asyncio
async def test_gets_fine_tuned_model_using_openai_client():
    """Test retrieving fine-tuned models using the OpenAI client."""
    client = AsyncOpenAI(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = (await client.models.list()).data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None

    model = await client.models.retrieve(first_model.id)

    assert model.id is not None
