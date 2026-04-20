from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from datetime import datetime
from slowapi.errors import RateLimitExceeded

def setup_error_handlers(app: FastAPI):
 
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"success": False,"error": "Internal server error","timestamp": datetime.utcnow().isoformat()})
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code,content={ "success": False, "error": exc.detail, "status_code": exc.status_code, "timestamp": datetime.utcnow().isoformat()})
    
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({"field": field,"message": error["msg"],"type": error["type"]})
        return JSONResponse(status_code=422,content={ "success": False, "error": "Validation failed", "details": errors, "timestamp": datetime.utcnow().isoformat()})
    
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        return JSONResponse(status_code=409,content={"success": False, "error": "Resource already exists", "message": "This record already exists in our system", "timestamp": datetime.utcnow().isoformat()})
    
    @app.exception_handler(ConnectionFailure)
    async def db_connection_handler(request: Request, exc: ConnectionFailure):
        return JSONResponse(status_code=503,content={"success": False,"error": "Service unavailable","message": "Database connection failed. Please try again later.","timestamp": datetime.utcnow().isoformat()})

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429,content={ "success": False, "error": "Rate limit exceeded", "message": "Too many requests. Please try again later.", "timestamp": datetime.utcnow().isoformat()})