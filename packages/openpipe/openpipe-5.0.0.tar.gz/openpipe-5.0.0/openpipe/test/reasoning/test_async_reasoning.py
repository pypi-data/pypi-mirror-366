import pytest
from dotenv import load_dotenv
import asyncio

from openpipe import AsyncOpenAI
from openpipe.test.test_config import TEST_LAST_LOGGED

load_dotenv()

client = AsyncOpenAI()


@pytest.fixture(autouse=True)
def setup():
    print("\nresetting async client\n")
    global client
    client = AsyncOpenAI()


async def test_async_reasoning_low_effort():
    completion = await client.chat.completions.create(
        model="o1",
        messages=[{"role": "system", "content": "count to 3"}],
        metadata={"prompt_id": "test_async_reasoning_low_effort"},
        reasoning_effort="low",
    )

    if not TEST_LAST_LOGGED:
        return

    await asyncio.sleep(0.1)
    last_logged = await client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
    assert last_logged.req_payload["messages"][0]["content"] == "count to 3"
    assert (
        last_logged.resp_payload["choices"][0]["message"]["content"]
        == completion.choices[0].message.content
    )
