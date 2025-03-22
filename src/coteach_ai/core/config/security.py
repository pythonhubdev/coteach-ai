import secrets

from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig

from .base import settings

cors_config: CORSConfig = CORSConfig(
	allow_origins=settings.app.ALLOWED_CORS_ORIGINS,  # type: ignore
	allow_methods=["*"],
	allow_credentials=True,
)

csrf_config: CSRFConfig = CSRFConfig(
	secret=secrets.token_urlsafe(32),
	cookie_name="csrftoken",
	cookie_path="/",
	header_name="X-CSRF-Token",
	cookie_secure=True,
	cookie_httponly=True,
	cookie_samesite="lax",
	cookie_domain=None,
	exclude=["/api/webhook", "/api/external"],
	exclude_from_csrf_key="exclude_from_csrf",
)
