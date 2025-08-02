from abc import ABC, abstractmethod
from typing import Any


class AbstractAPI(ABC):
    @abstractmethod
    def __init__(self, *, url: str, headers: dict[str, Any]) -> None: ...
