from openai import OpenAI

from openpipe.client import OpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)


def test_gets_fine_tuned_model_using_openpipe_client():
    """Test retrieving fine-tuned models using the OpenPipe client."""
    client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = client.list_models().data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None

    model = client.get_model(model_slug=first_model.id)

    assert model.id is not None


def test_gets_fine_tuned_model_using_openai_client():
    """Test retrieving fine-tuned models using the OpenAI client."""
    client = OpenAI(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = client.models.list().data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None

    model = client.models.retrieve(first_model.id)

    assert model.id is not None
