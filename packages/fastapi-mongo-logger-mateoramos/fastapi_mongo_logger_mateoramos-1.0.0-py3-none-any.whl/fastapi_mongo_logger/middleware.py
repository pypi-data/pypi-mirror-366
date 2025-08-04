import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import MongoLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: MongoLogger, log_request_body: bool = True, log_response_body: bool = False):
        super().__init__(app)
        self.logger = logger
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Capture request data
        request_body = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = json.loads(body.decode())
            except:
                request_body = "Unable to parse request body"

        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = (time.time() - start_time) * 1000

        # Capture response data
        response_body = None
        if self.log_response_body and hasattr(response, 'body'):
            try:
                response_body = json.loads(response.body.decode())
            except:
                response_body = "Unable to parse response body"

        # Log to MongoDB
        await self.logger.log_endpoint(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            response_time=process_time,
            request_body=request_body,
            response_body=response_body,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None
        )

        return response