import logging
import sys
from datetime import datetime
from typing import Any

from loguru import logger

from ..config.base import settings


class InterceptHandler(logging.Handler):
	def emit(self, record: logging.LogRecord) -> None:
		try:
			level: str | int = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		frame, depth = logging.currentframe(), 2
		while frame.f_code.co_filename == logging.__file__:
			if frame.f_back:
				frame = frame.f_back
				depth -= 1

		logger.opt(depth=depth, exception=record.exc_info).log(
			level,
			record.getMessage(),
		)


class CustomFormatter:
	def __call__(self, record: dict[str, Any]) -> str:
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		log_format = f"<green>{current_time}</green>"
		if record["function"]:
			log_format += " | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
		log_format += "- <level>{message}</level>\n"

		if record["exception"]:
			log_format += "{exception}\n"
		return log_format


def configure_logging() -> None:
	intercept_handler = InterceptHandler()
	intercept_handler.setFormatter(CustomFormatter())  # type: ignore
	logging.basicConfig(
		handlers=[intercept_handler],
		level=settings.log.LEVEL,
	)

	logger.configure(
		handlers=[
			{
				"sink": sys.stdout,
				"level": settings.log.LEVEL,
				"format": CustomFormatter(),
			},  # type:ignore
		],
	)


stage_logger = logger.bind(stage="STAGE")
end_stage_logger = logger.bind(stage="END STAGE")
