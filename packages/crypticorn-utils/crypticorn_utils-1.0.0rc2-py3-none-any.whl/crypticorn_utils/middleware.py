import time

from crypticorn_utils.metrics import has_migrated
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

if has_migrated:
    from crypticorn_utils.metrics import (
        HTTP_REQUEST_DURATION,
        HTTP_REQUESTS_COUNT,
        REQUEST_SIZE,
        RESPONSE_SIZE,
    )

    # otherwise prometheus reqisters metrics twice, resulting in an exception
    class PrometheusMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):

            if "authorization" in request.headers:
                auth_type = (
                    request.headers["authorization"].split()[0]
                    if " " in request.headers["authorization"]
                    else "none"
                )
            elif "x-api-key" in request.headers:
                auth_type = "X-API-KEY"
            else:
                auth_type = "none"

            try:
                endpoint = request.get(
                    "route"
                ).path  # use /time/{type} instead of dynamic route to avoid high cardinality
            except Exception:
                endpoint = request.url.path

            start = time.perf_counter()
            response = await call_next(request)
            duration = time.perf_counter() - start

            HTTP_REQUESTS_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                auth_type=auth_type,
            ).inc()

            try:
                body = await request.body()
                size = len(body)
            except Exception:
                size = 0

            REQUEST_SIZE.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(size)

            try:
                body = await response.body()
                size = len(body)
            except Exception:
                size = 0

            RESPONSE_SIZE.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(size)

            HTTP_REQUEST_DURATION.labels(
                endpoint=endpoint,
                method=request.method,
            ).observe(duration)

            return response


def add_middleware(app: "FastAPI"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https://([a-zA-Z0-9-]+.)*crypticorn.(dev|com)/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if has_migrated:
        app.add_middleware(PrometheusMiddleware)
