"""
middleware/response_standardizer.py — Response standardization middleware.
Globally intercepts and envelopes all API JSON responses into:
Success: { "success": true, "message": "...", "data": {...} }
Failure: { "success": false, "error": "...", "details": {...} }
"""
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool


class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """Starlette middleware to dynamically format and envelope all API JSON responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Bypass formatting for docs and static folders
        path = request.url.path
        if (
            path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
            or path.startswith("/static/")
            or path == "/health"
            or path == "/debug-db"
        ):
            return response

        # Standardize JSON responses
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                # Safely read response body
                if hasattr(response, "body") and response.body is not None:
                    raw_body = response.body
                else:
                    body_chunks = [chunk async for chunk in response.body_iterator]
                    response.body_iterator = iterate_in_threadpool(iter(body_chunks))
                    raw_body = b"".join(body_chunks)

                data = json.loads(raw_body.decode("utf-8"))

                # Skip if already formatted
                if isinstance(data, dict) and "success" in data and ("data" in data or "error" in data):
                    return response

                # Build standardized response envelope
                if response.status_code >= 400:
                    err_msg = data.get("detail", "Operation failed.") if isinstance(data, dict) else str(data)
                    standardized_body = {
                        "success": False,
                        "error": err_msg,
                        "details": data
                    }
                else:
                    standardized_body = {
                        "success": True,
                        "message": "Operation completed successfully.",
                        "data": data
                    }

                new_content = json.dumps(standardized_body).encode("utf-8")

                # Construct new response object
                new_response = Response(
                    content=new_content,
                    status_code=response.status_code,
                    media_type="application/json"
                )

                # Transfer existing headers excluding content-length
                for key, val in response.headers.items():
                    if key.lower() not in ("content-length", "content-type"):
                        new_response.headers[key] = val

                return new_response
            except Exception:
                # Return original unmodified response on any decoding/parsing failure
                return response

        return response
