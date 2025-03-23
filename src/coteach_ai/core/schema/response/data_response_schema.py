from typing import Any

from ..base import BaseResponseSchema


class DataResponseSchema(BaseResponseSchema):
	data: list[dict[str, Any]] | dict[str, Any] | str | None = None
	error: str | None = None
