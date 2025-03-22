from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from litestar import Litestar

from src.panorah_framework.database.connection import database
from src.panorah_framework.models import Base


class LifeSpan:
	@staticmethod
	@asynccontextmanager
	async def startup(app: Litestar) -> AsyncGenerator[None, None]:  # noqa: ARG004
		static_directory = Path.cwd().parent / "static"
		static_directory.mkdir(exist_ok=True)
		async with database.engine.begin() as conn:
			await conn.run_sync(Base.metadata.create_all)
		yield
