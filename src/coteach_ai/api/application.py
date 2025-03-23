from pathlib import Path

from litestar import Litestar
from litestar.static_files import create_static_files_router
from litestar_granian import GranianPlugin

from src.coteach_ai.api.lifespan import LifeSpan
from src.coteach_ai.core import Config, settings


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
		],
		middleware=[],
	)


app: Litestar = construct_app()
