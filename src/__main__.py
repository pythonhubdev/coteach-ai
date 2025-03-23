from dotenv import load_dotenv

from src.coteach_ai.api.application import app
from src.coteach_ai.api.granian_app import GranianApplication
from src.coteach_ai.api.hypercorn_app import HypercornApplication
from src.coteach_ai.core import configure_logging, settings


def main() -> None:
	"""Entrypoint of the application."""
	load_dotenv(".env")
	configure_logging()
	if settings.server.USE_HYPERCORN:
		hypercorn_app = HypercornApplication(app)
		hypercorn_app.run()
	else:
		GranianApplication.run()


if __name__ == "__main__":
	main()
