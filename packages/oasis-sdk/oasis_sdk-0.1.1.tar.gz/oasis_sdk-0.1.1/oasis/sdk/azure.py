from typing import Any, Optional

import httpx
from openai import RateLimitError as _RateLimitError
from openai import AsyncAzureOpenAI as _AsyncAzureOpenAI
from openai import AzureOpenAI as _AzureOpenAI

from ..base import OasisBase
from ..core.enums import Provider, ClientType
from ..errors import OasisRateLimitError
from ..core.client_factory import HttpxFactory


class OasisAzureOpenAI(OasisBase, _AzureOpenAI):
    """
    Azure OpenAI **동기** SDK 래퍼.
    """

    def __init__(
        self,
        *,
        user_id: str,
        workspace_code: str,
        tenant_code: str,
        proxy_url: str | None = None,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
        httpx_factory: Optional[HttpxFactory] = None,
        **azure_kw: Any,
    ) -> None:
    
        super().__init__(
            user_id=user_id,
            workspace_code=workspace_code,
            tenant_code=tenant_code,
            plugin_name=plugin_name,
            provider=Provider.AZURE,
            client_type=ClientType.SDK,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )

        self._httpx_factory = httpx_factory or self._httpx
        self._client: httpx.Client = self._httpx_factory.build_sync()

        azure_kw.setdefault("api_key", "proxy_handle")
        azure_kw.setdefault("azure_endpoint", self._resolve_base_url(proxy_url))
        azure_kw.setdefault("http_client", self._client)

        try:
            _AzureOpenAI.__init__(self, **azure_kw)
        except _RateLimitError as exc:  # Azure도 동일 예외 타입 사용
            raise OasisRateLimitError.from_openai(exc) from exc

        self._closed: bool = False

    def __enter__(self):
        base_enter = getattr(super(), "__enter__", None)
        if callable(base_enter):
            base_enter()
        return self

    def __exit__(self, exc_type, exc, tb):
        base_exit = getattr(super(), "__exit__", None)
        if callable(base_exit):
            base_exit(exc_type, exc, tb)
        self.close()

    def close(self) -> None:
        if not self._closed:
            self._client.close()
            self._closed = True


class OasisAsyncAzureOpenAI(OasisBase, _AsyncAzureOpenAI):
    """
    Azure OpenAI **비동기** SDK 래퍼.
    """

    def __init__(
        self,
        *,
        user_id: str,
        workspace_code: str,
        tenant_code: str,
        proxy_url: str | None = None,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
        httpx_factory: Optional[HttpxFactory] = None,
        **azure_kw: Any,
    ) -> None:
    
        super().__init__(
            user_id=user_id,
            workspace_code=workspace_code,
            tenant_code=tenant_code,
            plugin_name=plugin_name,
            provider=Provider.AZURE,
            client_type=ClientType.SDK,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )

        self._httpx_factory = httpx_factory or self._httpx
        self._async_client: httpx.AsyncClient = self._httpx_factory.build_async()

        azure_kw.setdefault("api_key", "proxy_handle")
        azure_kw.setdefault("azure_endpoint", self._resolve_base_url(proxy_url))
        azure_kw.setdefault("http_client", self._async_client)

        try:
            _AsyncAzureOpenAI.__init__(self, **azure_kw)
        except _RateLimitError as exc:
            raise OasisRateLimitError.from_openai(exc) from exc

        self._closed: bool = False

    async def __aenter__(self):
        base_enter = getattr(super(), "__aenter__", None)
        if callable(base_enter):
            await base_enter()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        base_exit = getattr(super(), "__aexit__", None)
        if callable(base_exit):
            await base_exit(exc_type, exc, tb)
        await self.aclose()

    async def aclose(self) -> None:
        if not self._closed:
            await self._async_client.aclose()
            self._closed = True
