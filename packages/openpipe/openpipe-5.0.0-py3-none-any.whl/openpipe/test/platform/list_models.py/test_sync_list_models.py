from openpipe.client import OpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)


def test_lists_models():
    """Test listing models and verifying model properties."""
    client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    models = client.list_models().data

    assert len(models) > 0

    first_model = models[0]

    assert first_model.id is not None
