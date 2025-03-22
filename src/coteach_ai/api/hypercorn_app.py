import asyncio

from coteach_ai.core import HypercornConfig
from hypercorn.asyncio import serve
from litestar import Litestar
from loguru import logger


class HypercornApplication:
	"""
	Custom Hypercorn application.

	This class is used to start Hypercorn with the Litestar application.
	"""

	def __init__(
		self,
		app: Litestar,
	) -> None:
		self.app = app

	def run(self) -> None:
		"""Run the FastAPI application with Hypercorn."""
		config = HypercornConfig()
		logger.info("Configuring Hypercorn Server...")
		logger.info(f"Starting Hypercorn Server on https://{config.bind[0]}")
		asyncio.run(serve(self.app, config))  # type: ignore
