from .lanchain_error import LangchainError


class DataError(LangchainError):
	def __init__(self, status: int, message: str, original_error: Exception | None = None):
		super().__init__(status, message, original_error)
