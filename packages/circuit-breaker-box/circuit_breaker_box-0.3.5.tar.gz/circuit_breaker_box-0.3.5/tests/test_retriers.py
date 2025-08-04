import typing

import fastapi.exceptions
import httpx
import pytest

from circuit_breaker_box import Retrier
from tests.conftest import SOME_HOST


async def test_retry(
    test_retry_without_circuit_breaker: Retrier[httpx.Response],
) -> None:
    test_request = httpx.AsyncClient().build_request(method="GET", url=SOME_HOST)

    async def bar(request: httpx.Request) -> httpx.Response:  # noqa: ARG001
        return httpx.Response(status_code=httpx.codes.OK)

    response = await test_retry_without_circuit_breaker.retry(bar, request=test_request)
    assert response.status_code == httpx.codes.OK

    async def foo(request: httpx.Request) -> typing.NoReturn:  # noqa: ARG001
        raise ZeroDivisionError

    with pytest.raises(ZeroDivisionError):
        await test_retry_without_circuit_breaker.retry(foo, request=test_request)


async def test_retry_custom_circuit_breaker(
    test_retry_custom_circuit_breaker_in_memory: Retrier[httpx.Response],
) -> None:
    test_request = httpx.AsyncClient().build_request(method="GET", url=SOME_HOST)

    async def bar(request: httpx.Request) -> httpx.Response:  # noqa: ARG001
        return httpx.Response(status_code=httpx.codes.OK)

    response = await test_retry_custom_circuit_breaker_in_memory.retry(bar, test_request.url.host, request=test_request)
    assert response.status_code == httpx.codes.OK

    async def foo(request: httpx.Request) -> typing.NoReturn:  # noqa: ARG001
        raise ZeroDivisionError

    with pytest.raises(fastapi.exceptions.HTTPException, match=f"500: Host: {test_request.url.host} is unavailable"):
        await test_retry_custom_circuit_breaker_in_memory.retry(foo, host=test_request.url.host, request=test_request)

    with pytest.raises(ValueError, match="'host' argument should be defined"):
        await test_retry_custom_circuit_breaker_in_memory.retry(
            foo,
            request=test_request,
            host="",
        )
