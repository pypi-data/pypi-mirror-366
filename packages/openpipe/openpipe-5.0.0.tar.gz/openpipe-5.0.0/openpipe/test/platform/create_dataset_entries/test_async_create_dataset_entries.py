import pytest
from datetime import datetime

from openpipe.client import AsyncOpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)

# Initialize the client
op_client = AsyncOpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)


@pytest.fixture
async def dataset_id():
    """Create a test dataset and return its ID."""
    dataset = await op_client.create_dataset(name="Test Dataset")
    yield dataset.id
    # Cleanup after tests
    await op_client.delete_dataset(dataset_id=dataset.id)


@pytest.fixture
async def reset_client():
    """Reset the client before each test."""
    global op_client
    op_client = AsyncOpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)
    return op_client


@pytest.mark.asyncio
class TestCreateDatasetEntries:
    @pytest.mark.asyncio
    async def test_add_entries_to_dataset(self, reset_client, dataset_id):
        """Test adding valid entries to a dataset."""
        entry = {
            "messages": [
                {"role": "user", "content": "Count to 7"},
                {"role": "assistant", "content": "1, 2, 3, 4, 5, 6, 7"},
            ],
            "split": "TRAIN",
            "metadata": {
                "prompt_id": "test-dataset-entry",
                "time": datetime.now().isoformat(),
            },
        }
        entries = [entry] * 10

        entry_creation = await op_client.create_dataset_entries(
            dataset_id, entries=entries
        )

        assert entry_creation.entries_created == 10
        assert len(entry_creation.errors.data) == 0

    @pytest.mark.asyncio
    async def test_add_entries_with_bad_metadata_fails(self, reset_client, dataset_id):
        """Test that adding entries with invalid metadata fails."""
        entry = {
            "messages": [
                {"role": "user", "content": "Count to 7"},
                {"role": "assistant", "content": "1, 2, 3, 4, 5, 6, 7"},
            ],
            "split": "TRAIN",
            "metadata": {"bad_key": 1, "time": datetime.now().isoformat()},
        }
        entries = [entry] * 10

        try:
            await op_client.create_dataset_entries(dataset_id, entries=entries)
        except Exception as e:
            print("e is", e)
            print(1)
            assert e.status_code == 400
            print(2)
            print(e.body["message"])
            assert "Input validation failed" in e.body["message"]
