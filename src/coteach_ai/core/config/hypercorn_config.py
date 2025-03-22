from typing import ClassVar

from hypercorn import Config

from .base import settings


class HypercornConfig(Config):
	bind: ClassVar[list[str]] = [f"{settings.server.HOST}:{settings.server.PORT}"]  # pyright: ignore [reportAssignmentType, reportIncompatibleMethodOverride]
	workers = settings.server.HTTP_WORKERS  # type: ignore
	use_reloader = settings.app.DEBUG
