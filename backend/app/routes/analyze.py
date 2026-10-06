from fastapi import APIRouter, Request

from app.models.schemas import ResumeTextRequest, SuccessResponse
from app.services.pdf_extractor import extract_upload_text, validate_resume_text
from app.services.resume_analysis import analyze_resume
from app.utils.errors import APIError


router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=SuccessResponse)
async def analyze(request: Request) -> SuccessResponse:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        career = str(form.get("career_field", "")).strip()
        if upload is None or not hasattr(upload, "read"):
            raise APIError(400, "FILE_REQUIRED", "Choose a PDF or TXT resume to continue.")
        text, _ = await extract_upload_text(upload)
    elif content_type.startswith("application/json"):
        try:
            payload = ResumeTextRequest.model_validate(await request.json())
        except ValueError as error:
            raise APIError(400, "INVALID_REQUEST", "Paste your resume and choose a career field to continue.") from error
        text, career = payload.resume_content, payload.career_field.strip()
    else:
        raise APIError(415, "INVALID_REQUEST", "Send either a PDF/TXT upload or pasted resume text.")
    if not career:
        raise APIError(400, "CAREER_REQUIRED", "Choose a career field before analyzing your resume.")
    return SuccessResponse(data=await analyze_resume(validate_resume_text(text), career))

