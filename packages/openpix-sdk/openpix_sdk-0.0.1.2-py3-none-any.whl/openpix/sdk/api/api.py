from typing import Any

from . import AbstractAPI


class API(AbstractAPI):
    def __init__(self, *, url: str, headers: dict[str, Any]) -> None:
        self._url = url
        self._headers = headers

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._url!r}, {self._headers!r})"
