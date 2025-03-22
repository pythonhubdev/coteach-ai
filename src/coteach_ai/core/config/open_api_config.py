from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from .base import settings
from .servers import server_config

open_api_config = OpenAPIConfig(
	title=settings.app.NAME,
	version="1.0",
	description="API for Panorah",
	servers=server_config,
	render_plugins=[
		ScalarRenderPlugin(
			js_url="/static/docs/scalar.js",
			css_url="/static/docs/scalar.css",
		),
	],
)
