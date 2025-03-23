class LangchainError(Exception):
	"""Base exception for all langchain related exceptions."""

	def __init__(self, status: int, message: str, original_error: Exception | None = None):
		self.status = status
		self.message = message
		self.original_error = original_error
		super().__init__(message)
