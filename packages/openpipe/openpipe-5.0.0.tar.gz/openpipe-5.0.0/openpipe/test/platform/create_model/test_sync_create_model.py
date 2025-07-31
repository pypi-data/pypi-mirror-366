import pytest
import time

from openpipe.client import OpenPipe
from openpipe.test.test_config import (
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)

# Constants
SFT_BASE_SLUG_DEPRECATED = "test-fine-tune3-deprecated"
SFT_BASE_SLUG = "test-fine-tune3"
SFT_CHECKPOINT_SLUG = "test-fine-tune3-checkpoint"
SFT_DPO_SLUG = "test-fine-tune3-dpo"

CONTENT_DATASET_ID = "11779bf9-580f-4bf3-914f-152aabf427db"

# Initialize the client
op_client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)


@pytest.fixture
def reset_client():
    """Reset the client before each test."""
    global op_client
    op_client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)
    return op_client


def try_deleting_model(model_slug):
    """Try deleting the model before each test."""
    try:
        op_client.delete_model(model_slug=model_slug)
    except Exception as e:
        print("caught exception")
        print(e)
        print("No fine tune to delete")


@pytest.mark.skip(
    reason="We don't want to keep creating a fine tune every time we run all tests"
)
def test_creates_fine_tune_with_deprecated_hyperparameters(reset_client):
    """Test creating a fine tune with deprecated hyperparameters."""
    try_deleting_model(SFT_BASE_SLUG_DEPRECATED)

    model = op_client.create_model(
        dataset_id=CONTENT_DATASET_ID,
        slug=SFT_BASE_SLUG_DEPRECATED,
        training_config={
            "provider": "openpipe",
            "baseModel": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "hyperparameters": {
                "batch_size": 16,
            },
        },
    )

    assert model.id == SFT_BASE_SLUG_DEPRECATED
    assert model.id is not None

    time.sleep(0.5)

    created_model = op_client.get_model(model_slug=model.id)
    assert created_model.openpipe.hyperparameters["batch_size"] == 16


@pytest.mark.skip(
    reason="We don't want to keep creating a fine tune every time we run all tests"
)
def test_creates_fine_tune_with_sft_hyperparameters(reset_client):
    """Test creating a fine tune with SFT hyperparameters."""
    try_deleting_model(SFT_BASE_SLUG)

    model = op_client.create_model(
        dataset_id=CONTENT_DATASET_ID,
        slug=SFT_BASE_SLUG,
        training_config={
            "provider": "openpipe",
            "baseModel": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "enable_sft": True,
            "enable_preference_tuning": False,
            "sft_hyperparameters": {
                "batch_size": "auto",
                "num_epochs": 3,
                "learning_rate_multiplier": 1,
            },
        },
    )

    assert model.id == SFT_BASE_SLUG
    assert model.id is not None

    time.sleep(0.5)

    created_model = op_client.get_model(model_slug=model.id)
    assert created_model.openpipe.hyperparameters["batch_size"] == "auto"


@pytest.mark.skip(
    reason="We don't want to keep creating a fine tune every time we run all tests"
)
def test_creates_fine_tune_from_base_checkpoint(reset_client):
    """Test creating a fine tune from base checkpoint using OpenPipe client."""
    try_deleting_model(SFT_CHECKPOINT_SLUG)

    model = op_client.create_model(
        dataset_id=CONTENT_DATASET_ID,
        slug=SFT_CHECKPOINT_SLUG,
        training_config={
            "provider": "openpipe",
            "baseModel": "llama-3-1-8b-content",
            "enable_sft": True,
            "enable_preference_tuning": False,
            "sft_hyperparameters": {
                "num_epochs": 1,
                "batch_size": 16,
            },
        },
    )

    assert model.id == SFT_CHECKPOINT_SLUG
    assert model.id is not None

    time.sleep(0.5)

    created_model = op_client.get_model(model_slug=model.id)
    assert created_model.openpipe.hyperparameters["batch_size"] == 16


@pytest.mark.skip(
    reason="We don't want to keep creating a fine tune every time we run all tests"
)
def test_creates_fine_tune_with_dpo(reset_client):
    """Test creating a fine tune from base checkpoint using DPO with OpenPipe client."""
    try_deleting_model(SFT_DPO_SLUG)
    model = op_client.create_model(
        dataset_id=CONTENT_DATASET_ID,
        slug=SFT_DPO_SLUG,
        training_config={
            "provider": "openpipe",
            "baseModel": "llama-3-1-8b-content",
            "enable_sft": True,
            "enable_preference_tuning": True,
            "sft_hyperparameters": {
                "num_epochs": 1,
                "batch_size": 16,
            },
            "preference_hyperparameters": {
                "num_epochs": 1,
            },
        },
    )

    assert model.id == SFT_DPO_SLUG
    assert model.id is not None

    time.sleep(0.5)

    created_model = op_client.get_model(model_slug=model.id)
    assert created_model.openpipe.hyperparameters["batch_size"] == 16


# @pytest.mark.skip()
def test_errors_when_preference_hyperparameters_provided_but_not_enabled(
    reset_client,
):
    """Test that an error occurs when preference hyperparameters are provided but not enabled."""
    try_deleting_model(SFT_DPO_SLUG)
    with pytest.raises(Exception) as excinfo:
        op_client.create_model(
            dataset_id=CONTENT_DATASET_ID,
            slug=SFT_DPO_SLUG,
            training_config={
                "provider": "openpipe",
                "baseModel": "llama-3-1-8b-content",
                "enable_sft": True,
                "enable_preference_tuning": False,
                "sft_hyperparameters": {
                    "num_epochs": 1,
                    "batch_size": 16,
                },
                "preference_hyperparameters": {
                    "num_epochs": 1,
                },
            },
        )

    assert excinfo.value.status_code == 400


# @pytest.mark.skip()
def test_errors_when_trying_to_preference_tune_non_dpo_model(reset_client):
    """Test that an error occurs when trying to preference tune a non-DPO model."""
    try_deleting_model(SFT_DPO_SLUG)

    with pytest.raises(Exception) as excinfo:
        op_client.create_model(
            dataset_id=CONTENT_DATASET_ID,
            slug=SFT_DPO_SLUG,
            training_config={
                "provider": "openpipe",
                "baseModel": "llama-3-1-70b-content",
                "enable_sft": True,
                "enable_preference_tuning": True,
                "sft_hyperparameters": {
                    "num_epochs": 1,
                    "batch_size": 16,
                },
                "preference_hyperparameters": {
                    "num_epochs": 1,
                },
            },
        )

    assert excinfo.value.status_code == 400
