from typing import Annotated

from litestar.dto import DTOConfig, MsgspecDTO

from ..base import BaseResponseSchema
from ..response.data_response_schema import DataResponseSchema

dto_config = DTOConfig(
	rename_strategy="camel",
)


class BaseResponseSchemaDTO(MsgspecDTO[Annotated[BaseResponseSchema, dto_config]]): ...


class DataResponseDTO(MsgspecDTO[Annotated[DataResponseSchema, dto_config]]): ...
