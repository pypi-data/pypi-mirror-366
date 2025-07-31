from __future__ import annotations

import contextlib
from typing import Iterator, AsyncIterator

import httpx

from .context import RequestContext
from .transports import HeaderTransport  # import 경로 확인


class HttpxFactory:
    """
    RequestContext로부터 httpx Client/AsyncClient를 생성.
    """

    def __init__(self, ctx: RequestContext, *, timeout: float = 30.0) -> None:
        self._ctx = ctx
        self._timeout = timeout

    @contextlib.contextmanager
    def client(self) -> Iterator[httpx.Client]:
        with httpx.Client(
            transport=HeaderTransport(self._ctx, inner=httpx.HTTPTransport()),
            timeout=self._timeout,
        ) as client:
            yield client

    def build_sync(self) -> httpx.Client:
        return httpx.Client(
            transport=HeaderTransport(self._ctx, inner=httpx.HTTPTransport()),
            timeout=self._timeout,
        )

    @contextlib.asynccontextmanager
    async def async_client(self) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            transport=HeaderTransport(self._ctx, inner=httpx.AsyncHTTPTransport()),
            timeout=self._timeout,
        ) as client:
            yield client

    def build_async(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=HeaderTransport(self._ctx, inner=httpx.AsyncHTTPTransport()),
            timeout=self._timeout,
        )
