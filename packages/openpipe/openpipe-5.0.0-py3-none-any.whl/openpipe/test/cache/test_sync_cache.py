import os
from dotenv import load_dotenv
import time
import random
from openai import OpenAI as BaseOpenAI

from openpipe import OpenAI
from openpipe.test.test_config import TEST_LAST_LOGGED

load_dotenv()

base_client = BaseOpenAI(
    base_url=os.environ["OPENPIPE_BASE_URL"], api_key=os.environ["OPENPIPE_API_KEY"]
)
client = OpenAI()


def generate_random_letters():
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(10)])


def test_sync_stable_cache_hit():
    messages = [{"role": "system", "content": "count to 10"}]
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        metadata={"prompt_id": "test_sync_stable_cache_hit"},
        store=True,
        openpipe={"cache": "readWrite"},
    )
    time.sleep(0.1)

    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        metadata={"prompt_id": "test_sync_stable_cache_hit"},
        store=True,
        openpipe={"cache": "readWrite"},
    )

    if not TEST_LAST_LOGGED:
        return


def test_sync_openai_call_caches_openpipe_client():
    models = ["gpt-4o-mini", "openpipe:test-content-35"]

    for model in models:
        messages = [
            {"role": "system", "content": f"{generate_random_letters()} count to 10"}
        ]
        client.chat.completions.create(
            model=model,
            messages=messages,
            store=True,
            metadata={"prompt_id": "test_sync_openai_call_caches_openpipe_client"},
        )
        time.sleep(0.1)

        client.chat.completions.create(
            model=model,
            messages=messages,
            store=True,
            metadata={"prompt_id": "test_sync_openai_call_caches_openpipe_client"},
        )

        if not TEST_LAST_LOGGED:
            return

        time.sleep(0.1)

        last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
        assert last_logged.cache_hit == False

        client.chat.completions.create(
            model=model,
            messages=messages,
            metadata={"prompt_id": "test_sync_openai_call_caches_openpipe_client"},
            store=True,
            openpipe={"cache": "readWrite"},
        )
        time.sleep(0.1)

        client.chat.completions.create(
            model=model,
            messages=messages,
            metadata={"prompt_id": "test_sync_openai_call_caches_openpipe_client"},
            store=True,
            openpipe={"cache": "readWrite"},
        )

        time.sleep(0.1)

        last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
        assert last_logged.cache_hit == True


def test_sync_openai_call_caches_base_client():
    models = ["gpt-4o-mini", "openpipe:test-content-35"]

    for model in models:
        messages = [
            {"role": "system", "content": f"{generate_random_letters()} count to 10"}
        ]
        base_client.chat.completions.create(
            model=model,
            messages=messages,
            store=True,
            metadata={"prompt_id": "test_sync_openai_call_caches_base_client"},
        )
        time.sleep(0.1)

        base_client.chat.completions.create(
            model=model,
            messages=messages,
            store=True,
            metadata={"prompt_id": "test_sync_openai_call_caches_base_client"},
        )

        if not TEST_LAST_LOGGED:
            return

        time.sleep(0.1)

        last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
        assert last_logged.cache_hit == False

        base_client.chat.completions.create(
            model=model,
            messages=messages,
            metadata={"prompt_id": "test_sync_openai_call_caches_base_client"},
            store=True,
            extra_headers={"op-cache": "readWrite"},
        )
        time.sleep(0.1)

        base_client.chat.completions.create(
            model=model,
            messages=messages,
            metadata={"prompt_id": "test_sync_openai_call_caches_base_client"},
            store=True,
            extra_headers={"op-cache": "readWrite"},
        )

        time.sleep(0.1)

        last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
        assert last_logged.cache_hit == True


def test_sync_read_only_avoids_writing_to_cache():
    messages = [
        {"role": "system", "content": f"{generate_random_letters()} count to 10"}
    ]

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_read_only_avoids_writing_to_cache"},
        store=True,
        openpipe={"cache": "readOnly"},
    )
    time.sleep(0.1)

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_read_only_avoids_writing_to_cache"},
        store=True,
        openpipe={"cache": "readOnly"},
    )

    if not TEST_LAST_LOGGED:
        return

    time.sleep(0.1)

    last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
    assert last_logged.cache_hit == False


def test_sync_write_only_avoids_reading_from_cache():
    messages = [
        {"role": "system", "content": f"{generate_random_letters()} count to 10"}
    ]

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_write_only_avoids_reading_from_cache"},
        store=True,
        openpipe={"cache": "writeOnly"},
    )
    time.sleep(0.1)

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_write_only_avoids_reading_from_cache"},
        store=True,
        openpipe={"cache": "writeOnly"},
    )

    if not TEST_LAST_LOGGED:
        return

    time.sleep(0.1)

    last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
    assert last_logged.cache_hit == False


def test_sync_write_read_work_together():
    messages = [
        {"role": "system", "content": f"{generate_random_letters()} count to 10"}
    ]

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_write_read_work_together"},
        store=True,
        openpipe={"cache": "writeOnly"},
    )
    time.sleep(0.1)

    client.chat.completions.create(
        model="openpipe:test-content-35",
        messages=messages,
        metadata={"prompt_id": "test_sync_write_read_work_together"},
        store=True,
        openpipe={"cache": "readOnly"},
    )

    if not TEST_LAST_LOGGED:
        return

    time.sleep(0.1)

    last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
    assert last_logged.cache_hit == True
