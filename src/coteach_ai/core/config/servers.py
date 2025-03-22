from litestar.openapi.spec import Server

from .base import settings

if settings.app.DEBUG:
	server_config = [
		Server(
			url="http://0.0.0.0:8000",
			description="Development server (0.0.0.0)",
		),
		Server(
			url="http://127.0.0.1:8000",
			description="Development server (localhost)",
		),
	]
else:
	server_config = [
		Server(
			url="https://api.coteach.com",
			description="Production server",
		),
		Server(
			url="http://127.0.0.1:8000",
			description="Development server (localhost)",
		),
	]
