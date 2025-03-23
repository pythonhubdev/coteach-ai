from msgspec import Struct
from msgspec.json import decode, encode

from ..constants.app_enums import StatusEnum


class BaseSchema(Struct, omit_defaults=True):
	"""Base class for all schemas with a unified to_dict method."""

	def to_dict(self) -> dict:
		return decode(encode(self))


class BaseResponseSchema(BaseSchema):
	message: str
	status: StatusEnum
