from typing import Any, AsyncIterator

import json_stream
from aiohttp import ClientSession, ClientResponse

from . import AsyncStreamAdapter


class HTTPClient:
    def __init__(self, *, base_url: str = "", headers: dict[str, Any] = None) -> None:
        self._base_url = base_url
        self._headers = headers
        if self._headers is None:
            self._headers = {}
        self._session = ClientSession(base_url=base_url, headers=headers)

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        if not isinstance(base_url, str):
            raise TypeError("base url must be str")
        self._base_url = base_url

    @property
    def headers(self) -> dict[str, Any]:
        return self._headers

    @headers.setter
    def headers(self, headers: dict[str, Any]) -> None:
        if headers is None:
            self._headers = {}
        elif isinstance(headers, dict):
            self._headers = headers
        else:
            raise TypeError("headers must be dict or None")

    async def close(self) -> None:
        await self._session.close()

    @staticmethod
    async def __response(response: ClientResponse) -> Any:
        response.raise_for_status()
        return await response.json()

    async def request(
        self,
        *,
        method: str,
        url: str = None,
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> Any:
        if url is None:
            url = self.base_url
        if headers is None:
            headers = self.headers
        async with self._session.request(
            method=method, url=url, headers=headers, json=json
        ) as response:
            return await self.__response(response)

    async def get(self, *, url: str = None, headers: dict[str, Any] = None) -> Any:
        return await self.request(method="GET", url=url, headers=headers)

    async def post(
        self,
        *,
        url: str = None,
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> Any:
        return await self.request(method="POST", url=url, headers=headers, json=json)

    async def put(
        self,
        *,
        url: str = None,
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> Any:
        return await self.request(method="PUT", url=url, headers=headers, json=json)

    async def patch(
        self,
        *,
        url: str = None,
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> Any:
        return await self.request(method="PATCH", url=url, headers=headers, json=json)

    async def delete(self, *, url: str = None, headers: dict[str, Any] = None) -> Any:
        return await self.request(method="DELETE", url=url, headers=headers)

    @staticmethod
    async def __stream_response(
        response: ClientResponse, json_path: str
    ) -> AsyncIterator:
        response.raise_for_status()
        stream_adapter = AsyncStreamAdapter(response.content.__aiter__())
        data = json_stream.load(stream_adapter)

        target_collection = None
        if not json_path or json_path == "item":
            target_collection = data
        else:
            current_level = data
            try:
                path_parts = json_path.split(".")
                for part in path_parts:
                    current_level = current_level[part]
                target_collection = current_level
            except (KeyError, AttributeError, TypeError, IndexError) as error:
                return
        if hasattr(target_collection, "__iter__") and not isinstance(
            target_collection, (str, bytes)
        ):
            for item in target_collection:
                yield item
        elif target_collection is not None:
            yield target_collection

    async def stream(
        self,
        *,
        method: str,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> AsyncIterator:
        if url is None:
            url = self.base_url
        if headers is None:
            headers = self.headers
        async with self._session.request(
            method=method, url=url, headers=headers, json=json
        ) as response:
            async for item in self.__stream_response(response, json_path):
                yield item

    async def stream_get(
        self,
        *,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
    ) -> AsyncIterator:
        async for item in self.stream(
            method="GET", url=url, json_path=json_path, headers=headers
        ):
            yield item

    async def stream_post(
        self,
        *,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> AsyncIterator:
        async for item in self.stream(
            method="POST", url=url, json_path=json_path, headers=headers, json=json
        ):
            yield item

    async def stream_put(
        self,
        *,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> AsyncIterator:
        async for item in self.stream(
            method="PUT", url=url, json_path=json_path, headers=headers, json=json
        ):
            yield item

    async def stream_patch(
        self,
        *,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> AsyncIterator:
        async for item in self.stream(
            method="PATCH", url=url, json_path=json_path, headers=headers, json=json
        ):
            yield item

    async def stream_delete(
        self,
        *,
        url: str = None,
        json_path: str = "item",
        headers: dict[str, Any] = None,
    ) -> AsyncIterator:
        async for item in self.stream(
            method="DELETE", url=url, json_path=json_path, headers=headers
        ):
            yield item

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"HTTPClient({self.base_url!r}, {self.headers!r})"
