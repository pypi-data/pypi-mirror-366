import contextlib
import logging
from collections.abc import Generator, Iterable
from itertools import chain, islice
from operator import itemgetter
from typing import Any

import h2.exceptions
import httpx
from fast_depends import inject
from httpx import Client
from pydantic import ValidationError
from tenacity import Retrying, before_sleep_log, retry_if_exception_type, stop_after_attempt, wait_exponential

from b24api.entity import ApiTypes, BatchResult, ErrorResponse, ListRequest, Request, Response
from b24api.error import RetryApiResponseError, RetryHTTPStatusError
from b24api.settings import ApiSettings


class Bitrix24:
    http: Client = Client(http2=True)

    @inject
    def __init__(self, settings: ApiSettings) -> None:
        self.settings = settings
        self.logger = logging.getLogger("b24api")

        self.http.timeout = self.settings.http_timeout

        self.retry = Retrying(
            retry=retry_if_exception_type(
                (
                    httpx.TransportError,
                    h2.exceptions.ProtocolError,
                    RetryHTTPStatusError,
                    RetryApiResponseError,
                ),
            ),
            wait=wait_exponential(multiplier=self.settings.retry_delay, exp_base=self.settings.retry_backoff),
            stop=stop_after_attempt(self.settings.retry_attempts),
            before_sleep=before_sleep_log(self.logger, logging.WARNING),
            reraise=True,
        )

    def call(self, request: Request | dict) -> ApiTypes:
        """Call any method (with retries) and return `result` from response."""
        return self.retry(self._call, request).result

    def _call(self, request: Request | dict) -> Response:
        """Call any method and return full response."""
        request = Request.model_validate(request)

        self.logger.debug("Sending request: %s", request)

        http_response = self.http.post(
            f"{self.settings.webhook_url}{request.method}",
            headers={"Content-Type": "application/json"},
            json=request.model_dump(mode="json")["parameters"],
        )

        with contextlib.suppress(httpx.ResponseNotRead, ValidationError):
            ErrorResponse.model_validate_json(http_response.content).raise_error(request, self.settings.retry_errors)

        try:
            http_response.raise_for_status()
        except httpx.HTTPStatusError as error:
            if http_response.status_code in self.settings.retry_statuses:
                raise RetryHTTPStatusError(
                    str(error),
                    request=error.request,
                    response=error.response,
                ) from error
            raise

        response = Response.model_validate_json(http_response.content)
        self.logger.debug("Received response: %s", response)

        return response

    def batch(
        self,
        requests: Iterable[Request | dict | tuple[Request | dict, Any]],
        *,
        batch_size: int | None = None,
        with_payload: bool = False,
    ) -> Generator[ApiTypes | tuple[ApiTypes, Any]]:
        """Call unlimited sequence of methods within batches and return `result` from responses."""
        batch_size = batch_size or self.settings.batch_size

        tail_requests = iter(requests)
        while batched_requests := list(islice(tail_requests, batch_size)):
            if with_payload:
                batched_requests, batched_payloads = zip(*batched_requests, strict=True)
            else:
                batched_payloads = None

            for i, response in enumerate(self.retry(self._batch, batched_requests)):
                if with_payload:
                    yield response.result, batched_payloads[i]
                else:
                    yield response.result

    def _batch(self, requests: Iterable[Request | dict]) -> list[Response]:
        """Call limited batch of methods and return full responses."""
        commands = {f"_{i}": Request.model_validate(request) for i, request in enumerate(requests)}
        request = Request(
            method="batch",
            parameters={
                "halt": True,
                "cmd": {key: request.query for key, request in commands.items()},
            },
        )

        result = self._call(request).result
        result = BatchResult.model_validate(result)

        responses = []
        for i in range(len(commands)):
            key = f"_{i}"

            if key in result.result_error:
                ErrorResponse.model_validate(result.result_error[key]).raise_error(
                    commands[key],
                    self.settings.retry_errors,
                )

            command = commands[key]
            if key not in result.result:
                raise ValueError(
                    f"Expecting `result` to contain result for command {{`{key}`: {command}}}. Got: {result}",
                )
            if key not in result.result_time:
                raise ValueError(
                    f"Expecting `result_time` to contain result for command {{`{key}`: {command}}}. Got: {result}",
                )

            responses.append(
                Response(
                    result=result.result[key],
                    time=result.result_time[key],
                    total=result.result_total.get(key, None),
                    next=result.result_next.get(key, None),
                ),
            )

        return responses

    def list_sequential(
        self,
        request: Request | dict,
        *,
        list_size: int | None = None,
    ) -> Generator[ApiTypes]:
        """Call `list` method and return full `result`.

        Slow (sequential tail) list gathering for methods without `filter` parameter (e.g. `department.get`).
        """
        request = Request.model_validate(request)
        list_size = list_size or self.settings.list_size

        head_request = request.model_copy(deep=True)
        head_request.parameters["start"] = 0

        head_response = self.retry(self._call, head_request)
        yield from self._fix_list_result(head_response.result)

        if head_response.next and head_response.next != list_size:
            raise ValueError(f"Expecting list chunk size to be {list_size}. Got: {head_response.next}")

        total = head_response.total or 0
        for start in range(list_size, total, list_size):
            tail_request = head_request.model_copy(deep=True)
            tail_request.parameters["start"] = start
            tail_response = self.retry(self._call, tail_request)

            if tail_response.next and tail_response.next != start + list_size:
                raise ValueError(
                    f"Expecting next list chunk to start at {start + list_size}. Got: {tail_response.next}",
                )
            yield from self._fix_list_result(tail_response.result)

    def list_batched(
        self,
        request: Request | dict,
        *,
        list_size: int | None = None,
        batch_size: int | None = None,
    ) -> Generator[ApiTypes]:
        """Call `list` method and return full `result`.

        Faster (batched tail) list gathering for methods without `filter` parameter (e.g. `department.get`).
        """
        request = Request.model_validate(request)
        list_size = list_size or self.settings.list_size
        batch_size = batch_size or self.settings.batch_size

        head_request = request.model_copy(deep=True)
        head_request.parameters["start"] = 0

        head_response = self.retry(self._call, head_request)
        yield from self._fix_list_result(head_response.result)

        if head_response.next and head_response.next != list_size:
            raise ValueError(f"Expecting chunk size to be {list_size}. Got: {head_response.next}")

        def _tail_requests() -> Generator[Request]:
            total = head_response.total or 0
            for start in range(list_size, total, list_size):
                tail_request = head_request.model_copy(deep=True)
                tail_request.parameters["start"] = start
                yield tail_request

        tail_responses = self.batch(_tail_requests(), batch_size=batch_size)
        tail_responses = map(self._fix_list_result, tail_responses)
        tail_responses = chain.from_iterable(tail_responses)
        yield from tail_responses

    def list_batched_no_count(
        self,
        request: ListRequest | dict,
        *,
        id_key: str = "ID",
        list_size: int | None = None,
        batch_size: int | None = None,
    ) -> Generator[ApiTypes]:
        """Call `list` method and return full `result`.

        Fastest (batched, no count) list gathering for methods with `filter` parameter (e.g. `crm.lead.list`).
        """
        request = ListRequest.model_validate(request)
        list_size = list_size or self.settings.list_size
        batch_size = batch_size or self.settings.batch_size

        select_ = request.parameters.select
        if "*" not in select_ and id_key not in select_:
            request.select.append(id_key)

        id_from, id_to = f">{id_key}", f"<{id_key}"
        get_id = itemgetter(id_key)

        filter_ = request.parameters.filter
        if filter_ and (id_from in filter_ or id_to in filter_):
            raise ValueError(
                f"Filter parameters `{id_from}` and `{id_to}` are reserved in `list_batched_no_count`",
            )

        if request.parameters.order:
            raise ValueError("Ordering parameters are reserved in `list_batched_no_count`")

        head_request = request.model_copy(deep=True)
        head_request.parameters.start = -1
        head_request.parameters.order = {"ID": "ASC"}

        tail_request = request.model_copy(deep=True)
        tail_request.parameters.start = -1
        tail_request.parameters.order = {"ID": "DESC"}

        head_tail_result = self.batch([head_request, tail_request], batch_size=batch_size)
        head_result, tail_result = tuple(map(self._fix_list_result, head_tail_result))
        yield from head_result

        max_head_id = max(map(int, map(get_id, head_result)), default=None)
        min_tail_id = min(map(int, map(get_id, tail_result)), default=None)

        def _body_requests() -> Generator[ListRequest]:
            for start in range(max_head_id, min_tail_id, list_size):
                body_request = head_request.model_copy(deep=True)
                body_request.parameters.filter[id_from] = start
                body_request.parameters.filter[id_to] = min(start + list_size + 1, min_tail_id)
                yield body_request

        if max_head_id and min_tail_id and max_head_id < min_tail_id:
            body = self.batch(_body_requests(), batch_size=batch_size)
            body = map(self._fix_list_result, body)
            body = chain.from_iterable(body)
            yield from body

        for item in reversed(tail_result):
            if int(get_id(item)) > max_head_id:
                yield item

    def reference_batched_no_count(
        self,
        request: ListRequest | dict,
        updates: Iterable[dict | tuple[dict, Any]],
        *,
        id_key: str = "ID",
        list_size: int | None = None,
        batch_size: int | None = None,
        with_payload: bool = False,
    ) -> Generator[ApiTypes | tuple[ApiTypes, Any]]:
        """Call `list` method with reference `updates` for `filter` and return full `result`.

        Fastest (batched, no count) list gathering for methods with `filter` parameter and required `reference`
        (e.g. `crm.timeline.comment.list`).
        """
        request = ListRequest.model_validate(request)
        list_size = list_size or self.settings.list_size
        batch_size = batch_size or self.settings.batch_size

        select_ = request.parameters.select
        if "*" not in select_ and id_key not in select_:
            request.select.append(id_key)

        id_from = f">{id_key}"
        get_id = itemgetter(id_key)

        filter_ = request.parameters.filter
        if filter_ and id_from in filter_:
            raise ValueError(
                f"Filter parameters `{id_from}` is reserved in `reference_batched_no_count`",
            )

        if request.parameters.order:
            raise ValueError("Ordering parameters are reserved `order`in `reference_batched_no_count`")

        def _tail_requests() -> Generator[ListRequest | tuple[ListRequest, Any]]:
            for update in updates:
                if with_payload:
                    update, payload = update
                else:
                    payload = None

                if id_from in update:
                    raise ValueError(
                        f"Filter parameters `{id_from}` is reserved in `reference_batched_no_count`",
                    )
                tail_request = request.model_copy(deep=True)
                tail_request.parameters.filter |= update
                tail_request.parameters.start = -1
                tail_request.parameters.order = {"ID": "ASC"}

                if with_payload:
                    yield tail_request, payload
                else:
                    yield tail_request

        head_requests = []
        tail_requests = iter(_tail_requests())
        while body_requests := head_requests + list(islice(tail_requests, batch_size - len(head_requests))):
            if with_payload:
                body_requests, body_payloads = zip(*body_requests, strict=True)
            else:
                body_payloads = None

            body_results = self.batch(body_requests, batch_size=batch_size)
            body_results = map(self._fix_list_result, body_results)

            head_requests = []
            for i, (body_request, body_result) in enumerate(zip(body_requests, body_results, strict=True)):
                if len(body_result) == list_size:
                    max_id = max(map(int, map(get_id, body_result)), default=None)
                    head_request = body_request.model_copy(deep=True)
                    head_request.parameters.filter[id_from] = max_id
                    if with_payload:
                        head_requests.append((head_request, body_payloads[i]))
                    else:
                        head_requests.append(head_request)

                if with_payload:
                    body_payload = [body_payloads[i]] * len(body_result)
                    body_result = zip(body_result, body_payload, strict=True)

                yield from body_result

    @staticmethod
    def _fix_list_result(result: list | dict[str, list]) -> list:
        """Fix `list` method result to `list of items` structure.

        There are two kinds of what `list` method `result` may contain:
        - a list of items (e.g. `department-get` and `disk.folder.getchildren`),
        - a dictionary with single item that contains the desired list of items
            (e.g. `tasks` in `tasks.task.list`).
        """
        if not isinstance(result, list | dict):
            raise TypeError(f"Expecting `result` to be a `list` or a `dict`. Got: {result}")

        if not result:
            return []

        if isinstance(result, list):
            return result

        if len(result) != 1:
            raise TypeError(
                f"If `result` is a `dict`, expecting single item. Got: {result}",
            )

        key = next(iter(result))
        value = result[key]

        if not isinstance(value, list):
            raise TypeError(f"If `result` is a `dict`, expecting single item to be a `list`. Got: {result}")

        return value
