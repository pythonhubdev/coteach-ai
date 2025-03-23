from litestar.openapi.spec import Server

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
