from openai import (
    AsyncOpenAI as OriginalAsyncOpenAI,
    ContentFilterFinishReasonError,
    LengthFinishReasonError,
    OpenAIError,
    APIError as OpenAIAPIError,
    Timeout,
)
from openai.resources import AsyncChat
from openai.resources.chat.completions import AsyncCompletions
from openai._streaming import AsyncStream
from openai._base_client import DEFAULT_MAX_RETRIES
from openai.lib._parsing import (
    ResponseFormatT,
    validate_input_tools,
    parse_chat_completion,
    type_to_response_format_param,
)
from openai._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from openai.types.chat import (
    completion_create_params,
    ChatCompletionAudioParam,
    ChatCompletionPredictionContentParam,
    ChatCompletionChunk,
)
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.shared_params.metadata import Metadata
from openai.types.chat_model import ChatModel
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_stream_options_param import (
    ChatCompletionStreamOptionsParam,
)
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)

import json
import os
import time
from typing import Union, Mapping, Optional, Dict, List, Iterable
from typing_extensions import Literal
import httpx

from .merge_openai_chunks import merge_openai_chunks
from .shared import (
    OpenPipeChatCompletion,
    report_async,
    get_extra_headers,
    configure_openpipe_clients,
    get_chat_completion_json,
)

from .client import AsyncOpenPipe
from .api_client.core.api_error import ApiError as OpenPipeApiError

MISSING_OPENAI_API_KEY = "MISSING_OPENAI_API_KEY"


class AsyncCompletionsWrapper(AsyncCompletions):
    openpipe_reporting_client: AsyncOpenPipe
    openpipe_completions_client: OriginalAsyncOpenAI
    fallback_client: OriginalAsyncOpenAI

    def __init__(
        self,
        client: OriginalAsyncOpenAI,
        openpipe_reporting_client: AsyncOpenPipe,
        openpipe_completions_client: OriginalAsyncOpenAI,
        fallback_client: OriginalAsyncOpenAI,
    ) -> None:
        super().__init__(client)
        self.openpipe_reporting_client = openpipe_reporting_client
        self.openpipe_completions_client = openpipe_completions_client
        self.fallback_client = fallback_client

    async def create(
        self, *args, **kwargs
    ) -> Union[OpenPipeChatCompletion, AsyncStream[ChatCompletionChunk]]:
        openpipe_options = kwargs.pop("openpipe", {}) or {}

        requested_at = int(time.time() * 1000)
        model = kwargs.get("model", "")
        default_timeout = self.openpipe_completions_client.timeout

        if (
            model.startswith("openpipe:")
            or model.startswith("openai:")
            or model.startswith("anthropic:")
            or model.startswith("gemini:")
            or openpipe_options.get("cache") is not None
        ):
            extra_headers = get_extra_headers(kwargs, openpipe_options)

            try:
                return await self.openpipe_completions_client.chat.completions.create(
                    **kwargs, extra_headers=extra_headers
                )
            except Exception as e:
                if (
                    "fallback" in openpipe_options
                    and "model" in openpipe_options["fallback"]
                ):
                    kwargs["model"] = openpipe_options["fallback"]["model"]
                    kwargs["timeout"] = openpipe_options["fallback"].get(
                        "timeout", default_timeout
                    )
                    try:
                        chat_completion = (
                            await self.fallback_client.chat.completions.create(**kwargs)
                        )
                        return await self._handle_response(
                            chat_completion, kwargs, openpipe_options, requested_at
                        )
                    except Exception as e:
                        return await self._handle_error(
                            e, kwargs, openpipe_options, requested_at
                        )
                else:
                    raise e

        try:
            if self._client.api_key == MISSING_OPENAI_API_KEY:
                raise OpenAIError(
                    "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
                )

            # OpenAI does not accept metadata if store is false
            openai_compatible_kwargs = kwargs.copy()
            if (
                "metadata" in openai_compatible_kwargs
                and not openai_compatible_kwargs.get("store")
            ):
                del openai_compatible_kwargs["metadata"]

            chat_completion = await super().create(*args, **openai_compatible_kwargs)
            return await self._handle_response(
                chat_completion, kwargs, openpipe_options, requested_at
            )
        except Exception as e:
            return await self._handle_error(e, kwargs, openpipe_options, requested_at)

    async def parse(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        audio: Optional[ChatCompletionAudioParam] | NotGiven = NOT_GIVEN,
        response_format: type[ResponseFormatT] | NotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        modalities: Optional[List[Literal["text", "audio"]]] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam]
        | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ReasoningEffort] | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream_options: Optional[ChatCompletionStreamOptionsParam]
        | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        web_search_options: completion_create_params.WebSearchOptions
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        openpipe: Optional[Dict[str, Union[str, OriginalAsyncOpenAI]]] = None,
    ) -> ParsedChatCompletion[ResponseFormatT]:
        validate_input_tools(tools)

        error_message = f"OpenPipe cannot guarantee json schema for {model}. Use the 'chat.completions.create()' API instead."

        if isinstance(model, str) and (
            model.startswith("anthropic:") or model.startswith("gemini:")
        ):
            raise ValueError(error_message)

        extra_headers = {
            "X-Stainless-Helper-Method": "chat.completions.parse",
            **(extra_headers or {}),
        }

        raw_completion = await self._client.chat.completions.create(
            messages=messages,
            model=model,
            audio=audio,
            response_format=type_to_response_format_param(response_format),
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            metadata=metadata,
            modalities=modalities,
            n=n,
            parallel_tool_calls=parallel_tool_calls,
            prediction=prediction,
            presence_penalty=presence_penalty,
            reasoning_effort=reasoning_effort,
            seed=seed,
            service_tier=service_tier,
            stop=stop,
            store=store,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            web_search_options=web_search_options,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            openpipe=openpipe,
        )

        # Check if the content of each choice is valid JSON
        for choice in raw_completion.choices:
            # If the model stops generating tokens due to length or content filter, we throw the same errors as parse_chat_completion
            if choice.finish_reason == "length":
                raise LengthFinishReasonError(completion=raw_completion)
            if choice.finish_reason == "content_filter":
                raise ContentFilterFinishReasonError()

            if isinstance(choice.message.content, str):
                try:
                    json.loads(choice.message.content)
                except json.JSONDecodeError:
                    raise ValueError(error_message)

        try:
            parsed_completion = parse_chat_completion(
                response_format=response_format,
                chat_completion=raw_completion,
                input_tools=tools,
            )
        except Exception:
            raise ValueError(error_message)

        # Add OpenPipe metadata if available
        if hasattr(raw_completion, "openpipe"):
            parsed_completion.openpipe = raw_completion.openpipe

        return parsed_completion

    async def _handle_response(
        self, chat_completion, kwargs, openpipe_options, requested_at
    ):
        if isinstance(chat_completion, AsyncStream):

            async def _gen():
                assembled_completion = None
                try:
                    async for chunk in chat_completion:
                        assembled_completion = merge_openai_chunks(
                            assembled_completion, chunk
                        )
                        yield chunk
                finally:
                    try:
                        received_at = int(time.time() * 1000)
                        await report_async(
                            configured_client=self.openpipe_reporting_client,
                            openpipe_options=openpipe_options,
                            requested_at=requested_at,
                            received_at=received_at,
                            req_payload=kwargs,
                            resp_payload=get_chat_completion_json(assembled_completion),
                            status_code=200,
                        )
                    except Exception as e:
                        pass

            return _gen()
        else:
            received_at = int(time.time() * 1000)
            await report_async(
                configured_client=self.openpipe_reporting_client,
                openpipe_options=openpipe_options,
                requested_at=requested_at,
                received_at=received_at,
                req_payload=kwargs,
                resp_payload=get_chat_completion_json(chat_completion),
                status_code=200,
            )
            return chat_completion

    async def _handle_error(self, e, kwargs, openpipe_options, requested_at):
        received_at = int(time.time() * 1000)
        if isinstance(e, OpenPipeApiError) or isinstance(e, OpenAIAPIError):
            error_content = None
            error_message = ""
            try:
                error_content = e.body
                if isinstance(e.body, str):
                    error_message = error_content
                else:
                    error_message = error_content["message"]
            except:
                pass

            await report_async(
                configured_client=self.openpipe_reporting_client,
                openpipe_options=openpipe_options,
                requested_at=requested_at,
                received_at=received_at,
                req_payload=kwargs,
                resp_payload=error_content,
                error_message=error_message,
                status_code=e.status_code,
            )
        raise e


class AsyncChatWrapper(AsyncChat):
    def __init__(
        self,
        client: OriginalAsyncOpenAI,
        openpipe_reporting_client: AsyncOpenPipe,
        openpipe_completions_client: OriginalAsyncOpenAI,
        fallback_client: OriginalAsyncOpenAI,
    ) -> None:
        super().__init__(client)
        self.completions = AsyncCompletionsWrapper(
            client,
            openpipe_reporting_client,
            openpipe_completions_client,
            fallback_client,
        )


def get_api_key(api_key: Optional[str]) -> str:
    return api_key or os.getenv("OPENAI_API_KEY") or MISSING_OPENAI_API_KEY


class AsyncOpenAIWrapper(OriginalAsyncOpenAI):
    chat: AsyncChatWrapper
    openpipe_reporting_client: AsyncOpenPipe
    openpipe_completions_client: OriginalAsyncOpenAI

    # Support auto-complete
    def __init__(
        self,
        *,
        openpipe: Optional[Dict[str, Union[str, OriginalAsyncOpenAI]]] = None,
        api_key: Union[str, None] = None,
        organization: Union[str, None] = None,
        base_url: Union[str, httpx.URL, None] = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Union[Mapping[str, str], None] = None,
        default_query: Union[Mapping[str, object], None] = None,
        http_client: Union[httpx.Client, None] = None,
        _strict_response_validation: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            api_key=get_api_key(api_key),
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            **kwargs,
        )

        self.openpipe_reporting_client = AsyncOpenPipe()
        self.openpipe_completions_client = OriginalAsyncOpenAI(
            api_key=get_api_key(api_key),
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            **kwargs,
        )
        configure_openpipe_clients(
            self.openpipe_reporting_client, self.openpipe_completions_client, openpipe
        )

        self.fallback_client = (
            openpipe.get("fallback_client")
            if openpipe
            else OriginalAsyncOpenAI(
                api_key=get_api_key(api_key),
                organization=organization,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                default_headers=default_headers,
                default_query=default_query,
                http_client=http_client,
                _strict_response_validation=_strict_response_validation,
                **kwargs,
            )
        )

        self.chat = AsyncChatWrapper(
            self,
            self.openpipe_reporting_client,
            self.openpipe_completions_client,
            self.fallback_client,
        )
