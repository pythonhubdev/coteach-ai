from time import time
from typing import TYPE_CHECKING

from src.coteach_ai.core.utils.logging import end_stage_logger, stage_logger
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import AbstractMiddleware
from litestar.types import Receive, Scope, Scopes, Send

if TYPE_CHECKING:
	from litestar.types import Message, Receive, Scope, Send


class LoggingMiddleware(AbstractMiddleware):
	scopes: Scopes = {ScopeType.HTTP}  # noqa: RUF012

	async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
		start_time = time()

		if scope["type"] == ScopeType.HTTP and scope.get("client"):
			stage_logger.info(
				f'{scope["client"][0]}:{scope["client"][1]} - "{scope["method"]} {scope["path"]} '  # type: ignore
				f'{scope["http_version"]}"',
			)

		async def send_wrapper(message: "Message") -> None:
			if message["type"] == "http.response.start":
				process_time = time() - start_time
				headers = MutableScopeHeaders.from_message(message=message)
				headers["X-Process-Time"] = str(process_time)

				if scope.get("client"):
					end_stage_logger.info(
						f'{scope["client"][0]}:{scope["client"][1]} - "{scope["method"]} '  # type: ignore
						f"{scope['path']} "  # type: ignore
						f'{scope["http_version"]}" {message["status"]}',
					)
			await send(message)

		await self.app(scope, receive, send_wrapper)
