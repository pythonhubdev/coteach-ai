from loguru import logger

from src.coteach_ai.agent import orchestrator
from src.coteach_ai.core import DataResponseSchema, StatusEnum
from src.coteach_ai.errors import DataError, InitializationError, InvalidSearchToolError, UnKnownModelError

from .schema import CourseCreateRequestSchema


class CourseGenController:
	@staticmethod
	async def create_course(request: CourseCreateRequestSchema) -> DataResponseSchema:
		try:
			logger.info(f"Generating course for description: {request.course_description}")
			result = await orchestrator.run(request.course_description)
			if not result or "course" not in result:
				msg = "Course generation failed to produce valid output"
				raise DataError(message=msg, status=500)
			logger.info("Course generation completed successfully")
			return DataResponseSchema(
				data={"course": result["course"]},
				message="Course generated successfully",
				status=StatusEnum.SUCCESS,
			)
		except (
			InitializationError,
			InvalidSearchToolError,
			UnKnownModelError,
			DataError,
		) as custom_exception:
			logger.error(custom_exception.message)
			return DataResponseSchema(
				message=custom_exception.message,
				status=StatusEnum.ERROR,
				error=str(custom_exception),
			)
		except Exception as exception:  # noqa: BLE001
			logger.error(f"Unknown error occurred: {exception}")
			return DataResponseSchema(
				message="Unknown error occurred",
				status=StatusEnum.ERROR,
				error=str(exception),
			)
