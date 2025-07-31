import typing
import os
from importlib.metadata import version

from openai import NOT_GIVEN
from openpipe.api_client.types.create_model_response import CreateModelResponse
from .api_client.types.create_dataset_entries_request_entries_item import (
    CreateDatasetEntriesRequestEntriesItem,
)
from .api_client.types.create_dataset_entries_response import (
    CreateDatasetEntriesResponse,
)
from .api_client.types.create_model_request_training_config import (
    CreateModelRequestTrainingConfig,
)
from .api_client.types.delete_dataset_response import DeleteDatasetResponse
from .api_client.types.delete_model_response import DeleteModelResponse
from .api_client.types.get_model_response import GetModelResponse
from .api_client.types.list_datasets_response import ListDatasetsResponse
from .api_client.types.list_models_response import ListModelsResponse
from .api_client.types.create_dataset_response import CreateDatasetResponse

from .api_client.client import (
    OpenPipeApi,
    AsyncOpenPipeApi,
    ReportResponse,
    ReportRequestTagsValue,
    ReportAnthropicResponse,
    UpdateLogTagsRequestFiltersItem,
    UpdateLogTagsRequestTagsValue,
    UpdateLogTagsResponse,
    GetCriterionJudgementRequestInput,
    GetCriterionJudgementRequestOutput,
    GetCriterionJudgementResponse,
)

OMIT = typing.cast(typing.Any, ...)

DEFAULT_BASE_URL = "https://api.openpipe.ai/api/v1"


def add_sdk_info(tags):
    tags["$sdk"] = "python"
    tags["$sdk.version"] = version("openpipe")
    return tags


# Remove any key from the dictionary that has a value of NOT_GIVEN
def remove_not_given(obj: typing.Dict | None) -> typing.Dict | None:
    # ensure obj is dict
    if not isinstance(obj, dict):
        return obj
    return {k: v for k, v in obj.items() if v != NOT_GIVEN}


class OpenPipe:
    base_client: OpenPipeApi

    def __init__(
        self,
        api_key: typing.Union[str, None] = None,
        base_url: typing.Union[str, None] = None,
        timeout: typing.Union[float, None] = None,
    ) -> None:
        self.base_client = OpenPipeApi(
            token="", base_url=DEFAULT_BASE_URL, timeout=timeout
        )
        # set API key
        if os.environ.get("OPENPIPE_API_KEY"):
            self.base_client._client_wrapper._token = os.environ["OPENPIPE_API_KEY"]
        if api_key:
            self.base_client._client_wrapper._token = api_key

        # set base URL
        if os.environ.get("OPENPIPE_BASE_URL"):
            self.base_client._client_wrapper._base_url = os.environ["OPENPIPE_BASE_URL"]
        if base_url:
            self.base_client._client_wrapper._base_url = base_url

    @property
    def api_key(self) -> typing.Union[str, None]:
        """Property getter for api_key."""
        return self.base_client._client_wrapper._token

    @api_key.setter
    def api_key(self, value: typing.Union[str, None]) -> None:
        """Property setter for api_key."""
        self._api_key = value
        if value is not None:
            self.base_client._client_wrapper._token = value

    @property
    def base_url(self) -> typing.Union[str, None]:
        """Property getter for base_url."""
        return self.base_client._client_wrapper._base_url

    @base_url.setter
    def base_url(self, value: typing.Union[str, None]) -> None:
        """Property setter for base_url."""
        if value is not None:
            self.base_client._client_wrapper._base_url = value

    def report(
        self,
        *,
        requested_at: typing.Optional[float] = OMIT,
        received_at: typing.Optional[float] = OMIT,
        req_payload: typing.Optional[typing.Any] = OMIT,
        resp_payload: typing.Optional[typing.Any] = OMIT,
        status_code: typing.Optional[float] = OMIT,
        error_message: typing.Optional[str] = OMIT,
        tags: typing.Optional[typing.Dict[str, ReportRequestTagsValue]] = {},
    ) -> ReportResponse:
        return self.base_client.report(
            requested_at=requested_at,
            received_at=received_at,
            req_payload=remove_not_given(req_payload),
            resp_payload=resp_payload,
            status_code=status_code,
            error_message=error_message,
            tags=add_sdk_info(tags),
        )

    def report_anthropic(
        self,
        *,
        requested_at: typing.Optional[float] = OMIT,
        received_at: typing.Optional[float] = OMIT,
        req_payload: typing.Optional[typing.Any] = OMIT,
        resp_payload: typing.Optional[typing.Any] = OMIT,
        status_code: typing.Optional[float] = OMIT,
        error_message: typing.Optional[str] = OMIT,
        tags: typing.Optional[typing.Dict[str, ReportRequestTagsValue]] = {},
        metadata: typing.Optional[typing.Dict[str, ReportRequestTagsValue]] = {},
    ) -> ReportAnthropicResponse:
        return self.base_client.report_anthropic(
            requested_at=requested_at,
            received_at=received_at,
            req_payload=req_payload,
            resp_payload=resp_payload,
            status_code=status_code,
            error_message=error_message,
            tags=add_sdk_info(tags),
            metadata=add_sdk_info(metadata),
        )

    def update_log_tags(
        self,
        *,
        filters: typing.List[UpdateLogTagsRequestFiltersItem],
        tags: typing.Dict[str, UpdateLogTagsRequestTagsValue],
    ) -> UpdateLogTagsResponse:
        return self.base_client.update_log_tags(filters=filters, tags=tags)

    def update_log_metadata(
        self,
        *,
        filters: typing.List[UpdateLogTagsRequestFiltersItem],
        metadata: typing.Dict[str, UpdateLogTagsRequestTagsValue],
    ) -> UpdateLogTagsResponse:
        return self.base_client.update_log_metadata(filters=filters, metadata=metadata)

    def get_criterion_judgement(
        self,
        *,
        criterion_id: str,
        input: GetCriterionJudgementRequestInput,
        output: GetCriterionJudgementRequestOutput,
    ) -> GetCriterionJudgementResponse:
        return self.base_client.get_criterion_judgement(
            criterion_id=criterion_id, input=input, output=output
        )

    def create_dataset(
        self,
        *,
        name: str,
    ) -> CreateDatasetResponse:
        return self.base_client.create_dataset(name=name)

    def list_datasets(
        self,
    ) -> ListDatasetsResponse:
        return self.base_client.list_datasets()

    def delete_dataset(
        self,
        *,
        dataset_id: str,
    ) -> DeleteDatasetResponse:
        return self.base_client.delete_dataset(dataset_id=dataset_id)

    def create_dataset_entries(
        self,
        dataset_id: str,
        *,
        entries: typing.List[CreateDatasetEntriesRequestEntriesItem],
    ) -> CreateDatasetEntriesResponse:
        return self.base_client.create_dataset_entries(
            dataset_id=dataset_id, entries=entries
        )

    def create_model(
        self,
        *,
        dataset_id: str,
        slug: str,
        pruning_rule_ids: typing.Optional[typing.List[str]] = OMIT,
        training_config: CreateModelRequestTrainingConfig,
        default_temperature: typing.Optional[float] = OMIT,
    ) -> CreateModelResponse:
        return self.base_client.create_model(
            dataset_id=dataset_id,
            slug=slug,
            pruning_rule_ids=pruning_rule_ids,
            training_config=training_config,
            default_temperature=default_temperature,
        )

    def get_model(
        self,
        *,
        model_slug: str,
    ) -> GetModelResponse:
        return self.base_client.get_model(model_slug=model_slug)

    def list_models(
        self,
    ) -> ListModelsResponse:
        return self.base_client.list_models()

    def delete_model(
        self,
        *,
        model_slug: str,
    ) -> DeleteModelResponse:
        return self.base_client.delete_model(model_slug=model_slug)


class AsyncOpenPipe:
    base_client: AsyncOpenPipeApi

    def __init__(
        self,
        api_key: typing.Union[str, None] = None,
        base_url: typing.Union[str, None] = None,
        timeout: typing.Union[float, None] = None,
    ) -> None:
        self.base_client = AsyncOpenPipeApi(
            token="", base_url=DEFAULT_BASE_URL, timeout=timeout
        )
        # set API key
        if os.environ.get("OPENPIPE_API_KEY"):
            self.base_client._client_wrapper._token = os.environ["OPENPIPE_API_KEY"]
        if api_key:
            self.base_client._client_wrapper._token = api_key

        # set base URL
        if os.environ.get("OPENPIPE_BASE_URL"):
            self.base_client._client_wrapper._base_url = os.environ["OPENPIPE_BASE_URL"]
        if base_url:
            self.base_client._client_wrapper._base_url = base_url

    @property
    def api_key(self) -> typing.Union[str, None]:
        """Property getter for api_key."""
        return self.base_client._client_wrapper._token

    @api_key.setter
    def api_key(self, value: typing.Union[str, None]) -> None:
        """Property setter for api_key."""
        self._api_key = value
        if value is not None:
            self.base_client._client_wrapper._token = value

    @property
    def base_url(self) -> typing.Union[str, None]:
        """Property getter for base_url."""
        return self.base_client._client_wrapper._base_url

    @base_url.setter
    def base_url(self, value: typing.Union[str, None]) -> None:
        """Property setter for base_url."""
        if value is not None:
            self.base_client._client_wrapper._base_url = value

    async def report(
        self,
        *,
        requested_at: typing.Optional[float] = OMIT,
        received_at: typing.Optional[float] = OMIT,
        req_payload: typing.Optional[typing.Any] = OMIT,
        resp_payload: typing.Optional[typing.Any] = OMIT,
        status_code: typing.Optional[float] = OMIT,
        error_message: typing.Optional[str] = OMIT,
        tags: typing.Optional[typing.Dict[str, ReportRequestTagsValue]] = {},
    ) -> ReportResponse:
        return await self.base_client.report(
            requested_at=requested_at,
            received_at=received_at,
            req_payload=remove_not_given(req_payload),
            resp_payload=resp_payload,
            status_code=status_code,
            error_message=error_message,
            tags=add_sdk_info(tags),
        )

    async def report_anthropic(
        self,
        *,
        requested_at: typing.Optional[float] = OMIT,
        received_at: typing.Optional[float] = OMIT,
        req_payload: typing.Optional[typing.Any] = OMIT,
        resp_payload: typing.Optional[typing.Any] = OMIT,
        status_code: typing.Optional[float] = OMIT,
        error_message: typing.Optional[str] = OMIT,
        tags: typing.Optional[typing.Dict[str, ReportRequestTagsValue]] = {},
    ) -> ReportAnthropicResponse:
        return await self.base_client.report_anthropic(
            requested_at=requested_at,
            received_at=received_at,
            req_payload=req_payload,
            resp_payload=resp_payload,
            status_code=status_code,
            error_message=error_message,
            tags=add_sdk_info(tags),
        )

    async def update_log_tags(
        self,
        *,
        filters: typing.List[UpdateLogTagsRequestFiltersItem],
        tags: typing.Dict[str, UpdateLogTagsRequestTagsValue],
    ) -> UpdateLogTagsResponse:
        return await self.base_client.update_log_tags(filters=filters, tags=tags)

    async def update_log_metadata(
        self,
        *,
        filters: typing.List[UpdateLogTagsRequestFiltersItem],
        metadata: typing.Dict[str, UpdateLogTagsRequestTagsValue],
    ) -> UpdateLogTagsResponse:
        return await self.base_client.update_log_metadata(
            filters=filters, metadata=metadata
        )

    async def get_criterion_judgement(
        self,
        *,
        criterion_id: str,
        input: GetCriterionJudgementRequestInput,
        output: GetCriterionJudgementRequestOutput,
    ) -> GetCriterionJudgementResponse:
        return await self.base_client.get_criterion_judgement(
            criterion_id=criterion_id, input=input, output=output
        )

    async def create_dataset(
        self,
        *,
        name: str,
    ) -> typing.Coroutine[typing.Any, typing.Any, CreateDatasetResponse]:
        return await self.base_client.create_dataset(name=name)

    async def list_datasets(
        self,
    ) -> typing.Coroutine[typing.Any, typing.Any, ListDatasetsResponse]:
        return await self.base_client.list_datasets()

    async def delete_dataset(
        self,
        *,
        dataset_id: str,
    ) -> typing.Coroutine[typing.Any, typing.Any, DeleteDatasetResponse]:
        return await self.base_client.delete_dataset(dataset_id=dataset_id)

    async def create_dataset_entries(
        self,
        dataset_id: str,
        *,
        entries: typing.List[CreateDatasetEntriesRequestEntriesItem],
    ) -> typing.Coroutine[typing.Any, typing.Any, CreateDatasetEntriesResponse]:
        return await self.base_client.create_dataset_entries(
            dataset_id=dataset_id, entries=entries
        )

    async def create_model(
        self,
        *,
        dataset_id: str,
        slug: str,
        pruning_rule_ids: typing.Optional[typing.List[str]] = OMIT,
        training_config: CreateModelRequestTrainingConfig,
        default_temperature: typing.Optional[float] = OMIT,
    ) -> typing.Coroutine[typing.Any, typing.Any, CreateModelResponse]:
        return await self.base_client.create_model(
            dataset_id=dataset_id,
            slug=slug,
            pruning_rule_ids=pruning_rule_ids,
            training_config=training_config,
            default_temperature=default_temperature,
        )

    async def get_model(
        self,
        *,
        model_slug: str,
    ) -> typing.Coroutine[typing.Any, typing.Any, GetModelResponse]:
        return await self.base_client.get_model(model_slug=model_slug)

    async def list_models(
        self,
    ) -> typing.Coroutine[typing.Any, typing.Any, ListModelsResponse]:
        return await self.base_client.list_models()

    async def delete_model(
        self,
        *,
        model_slug: str,
    ) -> typing.Coroutine[typing.Any, typing.Any, DeleteModelResponse]:
        return await self.base_client.delete_model(model_slug=model_slug)
