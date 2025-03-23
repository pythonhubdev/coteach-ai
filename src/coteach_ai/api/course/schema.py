from src.coteach_ai.core.schema.base import BaseSchema


class CourseCreateRequestSchema(BaseSchema):
	course_description: str
