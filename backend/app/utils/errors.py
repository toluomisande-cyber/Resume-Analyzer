from fastapi import Request
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": {"code": exc.code, "message": exc.message}})


async def unexpected_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"success": False, "error": {"code": "SERVER_ERROR", "message": "Something went wrong while analyzing the resume. Please try again."}})
