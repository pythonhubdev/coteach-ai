from loguru import logger

from src.coteach_ai.agent import orchestrator
from src.coteach_ai.core import DataResponseSchema, StatusEnum
from src.coteach_ai.errors import DataError, InitializationError, InvalidSearchToolError, UnKnownModelError

from .schema import CourseCreateRequestSchema


class CourseGenController:
	@staticmethod
	async def create_course(request: CourseCreateRequestSchema) -> DataResponseSchema:
		try:
			logger.info(f"Generating course for description: {request.brief}")
			result = await orchestrator.run(request.brief, request.target_audience)
			logger.info(f"Course generation completed successfully with result {result}")
			return DataResponseSchema(
				data=result,
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
				message="Unknown error occurred! Please try again sometimes the LLMs might not provide expected results",
				status=StatusEnum.ERROR,
				error=str(exception),
			)
