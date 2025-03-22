from .headers import response_headers
from .open_api_config import open_api_config
from .security import cors_config, csrf_config


class Config:
	RESPONSE_HEADERS = response_headers
	OPEN_API_CONFIG = open_api_config
	CORS_CONFIG = cors_config
	CSRF_CONFIG = csrf_config
