from litestar import Controller, post

from src.coteach_ai.api.course.controller import CourseGenController
from src.coteach_ai.api.course.dto import CourseCreateDTO
from src.coteach_ai.api.course.schema import CourseCreateRequestSchema
from src.coteach_ai.core import DataResponseDTO, DataResponseSchema


class CourseGenView(Controller):
	path = "/course"

	@post(
		"",
		dto=CourseCreateDTO,
		return_dto=DataResponseDTO,
	)
	async def generate_course(self, data: CourseCreateRequestSchema) -> DataResponseSchema:
		"""Generate a course with modules based on users topic."""
		return await CourseGenController.create_course(data)
