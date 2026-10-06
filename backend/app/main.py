from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.analyze import router as analyze_router
from app.utils.errors import APIError, api_error_handler, unexpected_error_handler


app = FastAPI(title="Resume Analyzer API", version="1.0.0")
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze_router)


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}
