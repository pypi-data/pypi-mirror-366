from typing import Any

from .api import API


class WebHookAPI(API):
    def __init__(self, url: str, headers: dict[str, Any]) -> None:
        super().__init__(url=url, headers=headers)
