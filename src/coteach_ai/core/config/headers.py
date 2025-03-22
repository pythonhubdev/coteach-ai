from collections.abc import Sequence

from litestar.datastructures import ResponseHeader

response_headers: Sequence[ResponseHeader] = [
	ResponseHeader(
		name="Cache-Control",
		value="no-cache, no-store, must-revalidate",
		description="Directs caching behavior for the client and intermediate caches. This setting prevents caching.",
	),
	ResponseHeader(
		name="Strict-Transport-Security",
		value="max-age=31536000; includeSubDomains; preload",
		description="Ensures that the browser only connects to the server over HTTPS, helping prevent protocol "
		"downgrade attacks.",
	),
	ResponseHeader(
		name="Content-Security-Policy",
		value=(
			"default-src 'self'; "
			"script-src 'self' 'unsafe-inline'; "
			"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
			"img-src 'self' data: https://cdn.jsdelivr.net; "
			"connect-src 'self'; "
			"font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; "
			"object-src 'none'; "
			"media-src 'self'; "
			"frame-ancestors 'none'; "
			"form-action 'self'; "
			"upgrade-insecure-requests;"
		),
		description="Helps prevent a wide range of attacks, including Cross-Site Scripting (XSS) and data injection "
		"attacks.",
	),
	ResponseHeader(
		name="X-Frame-Options",
		value="DENY",
		description="Prevents the page from being displayed in an iframe, protecting against clickjacking attacks.",
	),
	ResponseHeader(
		name="X-Content-Type-Options",
		value="nosniff",
		description="Prevents MIME type sniffing, ensuring the declared Content-Type is followed.",
	),
	ResponseHeader(
		name="Referrer-Policy",
		value="strict-origin-when-cross-origin",
		description="Controls how much referrer information should be included with requests.",
	),
	ResponseHeader(
		name="Access-Control-Allow-Methods",
		value="GET, POST, PUT, PATCH, DELETE, OPTIONS",
		description="Specifies which HTTP methods are allowed when accessing the resource in response to a preflight "
		"request.",
	),
	ResponseHeader(
		name="Access-Control-Allow-Headers",
		value="Content-Type, Authorization",
		description="Indicates which HTTP headers can be used during the actual request. Customize based on your APIs "
		"needs.",
	),
]
