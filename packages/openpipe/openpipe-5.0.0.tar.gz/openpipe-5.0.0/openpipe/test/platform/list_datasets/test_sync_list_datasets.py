from openpipe.client import OpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)


def test_lists_datasets():
    """Test listing datasets and verifying dataset properties."""
    client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

    # Create a test dataset
    test_dataset = client.create_dataset(
        name="Test Dataset for Listing",
    )

    try:
        # List datasets
        datasets = client.list_datasets()

        # Assertions
        assert datasets.data is not None
        assert isinstance(datasets.data, list)

        # Check if the test dataset is in the list
        found_test_dataset = next(
            (dataset for dataset in datasets.data if dataset.id == test_dataset.id),
            None,
        )
        assert found_test_dataset is not None

        # Verify dataset properties
        assert found_test_dataset.name == "Test Dataset for Listing"
        assert found_test_dataset.dataset_entry_count == 0
        assert found_test_dataset.fine_tune_count == 0
        assert found_test_dataset.created is not None
        assert found_test_dataset.updated is not None

    finally:
        # Clean up - delete the test dataset
        client.delete_dataset(dataset_id=test_dataset.id)
