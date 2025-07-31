from dotenv import load_dotenv

from openpipe import OpenAI
from openpipe.test.test_config import TEST_LAST_LOGGED

load_dotenv()

client = OpenAI()


def test_sync_reasoning_low_effort():
    completion = client.chat.completions.create(
        model="o1",
        messages=[{"role": "system", "content": "count to 3"}],
        metadata={"prompt_id": "test_sync_reasoning_low_effort"},
        reasoning_effort="low",
    )

    if not TEST_LAST_LOGGED:
        return

    last_logged = client.openpipe_reporting_client.base_client.local_testing_only_get_latest_logged_call()
    assert last_logged.req_payload["messages"][0]["content"] == "count to 3"
    assert (
        last_logged.resp_payload["choices"][0]["message"]["content"]
        == completion.choices[0].message.content
    )
