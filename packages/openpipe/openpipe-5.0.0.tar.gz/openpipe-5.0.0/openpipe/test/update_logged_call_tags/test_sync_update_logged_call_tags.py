import pytest
from dotenv import load_dotenv
import time
import random

from openpipe.client import OpenPipe
from openpipe.test.test_config import (
    TEST_LAST_LOGGED,
    OPENPIPE_BASE_URL,
    OPENPIPE_API_KEY,
)

load_dotenv()

op_client = OpenPipe(api_key=OPENPIPE_API_KEY, base_url=OPENPIPE_BASE_URL)

resp_payload = {
    "model": "gpt-4o",
    "usage": {
        "total_tokens": 39,
        "prompt_tokens": 11,
        "completion_tokens": 28,
    },
    "object": "chat.completion",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10",
            },
            "finish_reason": "stop",
        },
    ],
    "created": 1704449593,
}


def generate_random_id():
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(10)])


def last_logged_call():
    return op_client.base_client.local_testing_only_get_latest_logged_call()


def test_sync_adds_metadata():
    original_prompt_id = "original prompt id" + generate_random_id()

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {"prompt_id": original_prompt_id},
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    new_metadata = {
        "any_key": "any value",
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[{"field": "metadata.prompt_id", "equals": original_prompt_id}],
        metadata=new_metadata,
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == original_prompt_id
    assert last_logged.metadata["any_key"] == "any value"
    assert last_logged.metadata["otherId"] == "value 3"


def test_sync_updates_metadata():
    original_prompt_id = "original prompt id " + generate_random_id()

    payload1 = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }
    payload2 = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 2",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload1,
        resp_payload=None,
    )

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload2,
        resp_payload=None,
    )

    updated_metadata = {
        "prompt_id": "updated prompt id " + generate_random_id(),
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[{"field": "metadata.prompt_id", "equals": original_prompt_id}],
        metadata=updated_metadata,
    )

    assert resp.matched_logs == 2

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == updated_metadata["prompt_id"]
    assert last_logged.metadata["otherId"] == updated_metadata["otherId"]
    assert last_logged.metadata["any_key"] == "any value"


def test_sync_updates_metadata_by_completion_id():
    original_prompt_id = "original prompt id " + generate_random_id()
    completion_id = generate_random_id()
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload={
            "id": "other completion id",
            **resp_payload,
        },
    )

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload={
            "id": completion_id,
            **resp_payload,
        },
    )

    updated_metadata = {
        "prompt_id": "updated prompt id " + generate_random_id(),
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[{"field": "completionId", "equals": completion_id}],
        metadata=updated_metadata,
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == updated_metadata["prompt_id"]
    assert last_logged.metadata["otherId"] == updated_metadata["otherId"]
    assert last_logged.metadata["any_key"] == "any value"


def test_sync_updates_metadata_by_model():
    model = generate_random_id()
    original_prompt_id = "original prompt id " + generate_random_id()

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    updated_metadata = {
        "prompt_id": "updated prompt id " + generate_random_id(),
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[{"field": "model", "equals": model}],
        metadata=updated_metadata,
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == updated_metadata["prompt_id"]
    assert last_logged.metadata["otherId"] == updated_metadata["otherId"]
    assert last_logged.metadata["any_key"] == "any value"


def test_sync_updates_by_combination_of_filters():
    model = generate_random_id()
    original_prompt_id = "original prompt id " + generate_random_id()

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    updated_metadata = {
        "prompt_id": "updated prompt id " + generate_random_id(),
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[
            {"field": "model", "equals": model},
            {"field": "metadata.prompt_id", "equals": original_prompt_id},
        ],
        metadata=updated_metadata,
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == updated_metadata["prompt_id"]
    assert last_logged.metadata["otherId"] == updated_metadata["otherId"]
    assert last_logged.metadata["any_key"] == "any value"


def test_sync_updates_some_metadata_by_combination_of_filters():
    model = generate_random_id()
    other_model = "model-to-not-update"
    original_prompt_id = "original prompt id " + generate_random_id()

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload={
            **payload,
            "model": other_model,
        },
        resp_payload=None,
    )

    updated_metadata = {
        "prompt_id": "updated prompt id " + generate_random_id(),
        "otherId": "value 3",
    }

    resp = op_client.update_log_metadata(
        filters=[
            {"field": "model", "equals": model},
            {"field": "metadata.prompt_id", "equals": original_prompt_id},
        ],
        metadata=updated_metadata,
    )

    assert resp.matched_logs == 2

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == original_prompt_id
    assert last_logged.metadata["otherId"] == "value 1"
    assert last_logged.metadata["any_key"] == "any value"


def test_sync_deletes_metadata():
    keep_prompt_id = "prompt id for metadata to keep " + generate_random_id()
    delete_prompt_id = "prompt id for metadata to delete " + generate_random_id()

    payloadKeep = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": keep_prompt_id,
            "otherId": "value 1",
            "any_key": "any value",
        },
    }

    payloadDelete = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": delete_prompt_id,
            "otherId": "value 2",
            "any_key": "any value",
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payloadKeep,
        resp_payload=None,
    )

    keep_resp = op_client.update_log_metadata(
        filters=[{"field": "metadata.prompt_id", "equals": delete_prompt_id}],
        metadata={"prompt_id": None},
    )

    assert keep_resp.matched_logs == 0

    if not TEST_LAST_LOGGED:
        return

    keep_logged_call = last_logged_call()
    assert keep_logged_call.metadata["prompt_id"] == keep_prompt_id

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payloadDelete,
        resp_payload=None,
    )

    resp = op_client.update_log_metadata(
        filters=[{"field": "metadata.prompt_id", "equals": delete_prompt_id}],
        metadata={"prompt_id": None},
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata.get("prompt_id") == None


def test_sync_openpipe_deprecated_tags():
    original_prompt_id = generate_random_id()
    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=None,
        resp_payload=None,
        tags={
            "prompt_id": original_prompt_id,
            "otherId": "value 1",
        },
    )
    resp = op_client.update_log_tags(
        filters=[{"field": "tags.prompt_id", "equals": original_prompt_id}],
        tags={"otherId": "value 2"},
    )

    assert resp.matched_logs == 1

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    assert last_logged.metadata["prompt_id"] == original_prompt_id
    assert last_logged.metadata["otherId"] == "value 2"


def test_sync_deletes_nothing_when_no_metadata_matched():
    original_prompt_id = "id 1"
    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        resp_payload=None,
        req_payload={
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": "count to 3"}],
            "metadata": {"prompt_id": original_prompt_id},
        },
    )
    resp = op_client.update_log_metadata(
        filters=[{"field": "metadata.prompt_id", "equals": generate_random_id()}],
        metadata={"prompt_id": None},
    )

    assert resp.matched_logs == 0

    if not TEST_LAST_LOGGED:
        return

    last_logged = last_logged_call()
    print(last_logged.metadata)
    assert last_logged.metadata["prompt_id"] == original_prompt_id


# Deleting all logged calls will result in a timeout when run against
# a project with any sizeable number of logged calls.
@pytest.mark.skip()
def test_sync_deletes_from_all_logged_calls_when_no_filters_provided():
    prompt_id = generate_random_id()
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": "count to 3"}],
        "metadata": {
            "prompt_id": prompt_id,
        },
    }

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        req_payload=payload,
        resp_payload=None,
    )

    if not TEST_LAST_LOGGED:
        return

    op_client.report(
        requested_at=int(time.time() * 1000),
        received_at=int(time.time() * 1000),
        resp_payload=None,
        req_payload=payload,
    )

    resp = op_client.update_log_metadata(
        filters=[],
        metadata={"prompt_id": None},
    )

    assert resp.matched_logs >= 2

    last_logged = last_logged_call()
    assert last_logged.metadata.get("prompt_id") == None
