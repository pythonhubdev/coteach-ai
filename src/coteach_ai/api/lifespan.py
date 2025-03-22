from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from litestar import Litestar


class LifeSpan:
	@staticmethod
	@asynccontextmanager
	async def startup(app: Litestar) -> AsyncGenerator[None, None]:  # noqa: ARG004
		static_directory = Path.cwd().parent / "static"
		static_directory.mkdir(exist_ok=True)
		yield
