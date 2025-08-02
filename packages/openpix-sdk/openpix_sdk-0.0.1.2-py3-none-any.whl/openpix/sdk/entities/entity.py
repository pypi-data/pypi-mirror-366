from typing import Any

from pydantic import BaseModel


class Entity(BaseModel):
    def to_dict(
        self,
        *,
        mode: str = "python",
        include: set[str] = None,
        exclude: set[str] = None,
    ) -> dict[str, Any]:
        return self.model_dump(mode=mode, include=include, exclude=exclude)

    def to_json(
        self, *, indent: int = None, include: set[str] = None, exclude: set[str] = None
    ) -> str:
        return self.model_dump_json(indent=indent, include=include, exclude=exclude)
