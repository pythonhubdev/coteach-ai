from pathlib import Path

from litestar import Litestar, get
from litestar.static_files import create_static_files_router
from litestar_granian import GranianPlugin
from loguru import logger

from src.coteach_ai.api.course.view import CourseGenView
from src.coteach_ai.api.lifespan import LifeSpan
from src.coteach_ai.core import BaseResponseSchema, BaseResponseSchemaDTO, Config, StatusEnum, settings
from src.coteach_ai.middlewares import LoggingMiddleware


@get("/", return_dto=BaseResponseSchemaDTO)
async def health() -> BaseResponseSchema:
	return BaseResponseSchema(
		message="Welcome to CoTeach Course Generation AI API",
		status=StatusEnum.SUCCESS,
	)


def construct_app() -> Litestar:
	return Litestar(
		debug=settings.app.DEBUG,
		response_headers=Config.RESPONSE_HEADERS,
		allowed_hosts=settings.app.ALLOWED_CORS_ORIGINS,
		cors_config=Config.CORS_CONFIG,
		openapi_config=Config.OPEN_API_CONFIG,
		lifespan=[
			LifeSpan.startup,
		],
		plugins=[
			GranianPlugin(),
		],
		route_handlers=[
			create_static_files_router(
				path="/static/docs",
				directories=[
					Path(__file__).parent.parent / "static" / "docs",
				],
			),
			health,
			CourseGenView,
		],
		middleware=[
			LoggingMiddleware,
		],
	)


app: Litestar = construct_app()
if settings.app.DEBUG:
	logger.info(f"Checkout the docs at: http://{settings.server.HOST}:{settings.server.PORT}/schema")
else:
	logger.info(f"Checkout the docs at: https://{settings.server.HOST}:{settings.server.PORT}/schema")
