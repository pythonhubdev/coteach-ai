from coteach_ai.core import settings
from granian import Granian
from granian.constants import Interfaces


class GranianApplication:
	"""
	Custom Granian application.

	This class is used to start Granian with the Litestar application.
	"""

	@staticmethod
	def run() -> None:
		"""Run the FastAPI application with Hypercorn."""
		granian_app = Granian(
			target=settings.server.APP_LOC,
			interface=Interfaces.ASGI,
			address=settings.server.HOST,
			port=settings.server.PORT,
			workers=settings.server.HTTP_WORKERS,
			reload=settings.app.DEBUG,
			log_access=settings.app.DEBUG,
			log_enabled=settings.app.DEBUG,
			log_level=settings.log.MAPPED_LOG_LEVELS,
		)
		granian_app.serve()
