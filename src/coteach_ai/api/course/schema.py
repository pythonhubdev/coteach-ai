from src.coteach_ai.core.schema.base import BaseSchema


class CourseCreateRequestSchema(BaseSchema):
	brief: str
	target_audience: str
