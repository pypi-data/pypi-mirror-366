from dotenv import load_dotenv
import os
from openai import LengthFinishReasonError, OpenAI as BaseOpenAI

from openpipe import OpenAI
from openpipe.test.test_config import TEST_LAST_LOGGED
from pydantic import BaseModel

load_dotenv()

base_client = BaseOpenAI(
    base_url=os.environ["OPENPIPE_BASE_URL"], api_key=os.environ["OPENPIPE_API_KEY"]
)
client = OpenAI()


class PydanticType(BaseModel):
    name: str
    date: str


def test_sync_parse_success():
    completion = client.chat.completions.parse(
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

    last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()

    assert (
        last_logged.resp_payload["choices"][0]["message"]["content"]
        == completion.choices[0].message.content
    )


def test_sync_parse_error_due_to_length():
    try:
        client.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "system", "content": "count to 3"}],
            response_format=PydanticType,
            metadata={"prompt_id": "test_async_content"},
            max_tokens=1,
        )
        assert False
    except Exception as e:
        assert isinstance(e, LengthFinishReasonError)


def test_sync_parse_failure():
    try:
        client.chat.completions.parse(
            model="openpipe:llama-3-1-8b-content",
            messages=[{"role": "system", "content": "count to 3"}],
            response_format=PydanticType,
            metadata={"prompt_id": "test_async_content"},
        )
        assert False
    except Exception as e:
        print(e)
        pass
