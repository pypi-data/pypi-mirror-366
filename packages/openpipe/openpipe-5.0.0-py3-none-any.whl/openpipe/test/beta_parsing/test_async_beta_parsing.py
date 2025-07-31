import pytest
import os
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI as BaseAsyncOpenAI, LengthFinishReasonError
from pydantic import BaseModel

from openpipe import AsyncOpenAI
from openpipe.test.test_config import TEST_LAST_LOGGED

load_dotenv()

base_client = BaseAsyncOpenAI(
    base_url=os.environ["OPENPIPE_BASE_URL"], api_key=os.environ["OPENPIPE_API_KEY"]
)
client = AsyncOpenAI()


@pytest.fixture(autouse=True)
def setup():
    print("\nresetting async client\n")
    global client
    client = AsyncOpenAI()


class PydanticType(BaseModel):
    name: str
    date: str


async def test_async_parse_success():
    completion = await client.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "system", "content": "count to 3"}],
        response_format=PydanticType,
        metadata={"prompt_id": "test_async_content"},
    )

    parsed = completion.choices[0].message.parsed
    assert parsed.name is not None
    assert parsed.date is not None

    if not TEST_LAST_LOGGED:
        return

    await asyncio.sleep(0.1)
    last_logged = await client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()

    assert (
        last_logged.resp_payload["choices"][0]["message"]["content"]
        == completion.choices[0].message.content
    )


async def test_async_parse_error_due_to_length():
    try:
        await client.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "system", "content": "count to 3"}],
            response_format=PydanticType,
            metadata={"prompt_id": "test_async_content"},
            max_tokens=1,
        )
        assert False
    except Exception as e:
        assert isinstance(e, LengthFinishReasonError)


async def test_async_parse_failure():
    try:
        await client.chat.completions.parse(
            model="openpipe:llama-3-1-8b-content",
            messages=[{"role": "system", "content": "count to 3"}],
            response_format=PydanticType,
            metadata={"prompt_id": "test_async_content"},
        )
        assert False
    except Exception as e:
        print(e)
        pass
