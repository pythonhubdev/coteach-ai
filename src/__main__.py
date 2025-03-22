from coteach_ai.api.application import app
from coteach_ai.api.granian_app import GranianApplication
from coteach_ai.api.hypercorn_app import HypercornApplication
from coteach_ai.core import configure_logging, settings
from dotenv import load_dotenv


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
