from typing import Annotated

from litestar.dto import MsgspecDTO

from src.coteach_ai.core import dto_config

from .schema import CourseCreateRequestSchema


class CourseCreateDTO(MsgspecDTO[Annotated[CourseCreateRequestSchema, dto_config]]): ...
