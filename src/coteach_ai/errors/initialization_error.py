from .lanchain_error import LangchainError


class InitializationError(LangchainError):
	"""Exception raised during llm or tools initialization."""

	def __init__(self, status: int, message: str, original_error: Exception | None = None):
		super().__init__(status, message, original_error)
