from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader

from app.config import settings
from app.utils.errors import APIError


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def _extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1].lower()


async def extract_upload_text(upload: UploadFile) -> tuple[str, str]:
    filename = upload.filename or "resume"
    extension = _extension(filename)
    if extension not in SUPPORTED_EXTENSIONS:
        raise APIError(400, "UNSUPPORTED_FILE", "This file type isn't supported. Please upload a PDF or TXT file.")

    content = await upload.read(settings.max_upload_bytes + 1)
    if not content:
        raise APIError(400, "EMPTY_RESUME", "We couldn't find any resume content. Please upload another file or paste your resume.")
    if len(content) > settings.max_upload_bytes:
        raise APIError(413, "FILE_TOO_LARGE", "This file is too large. Please upload a file smaller than 5 MB.")

    if extension == ".txt":
        try:
            return content.decode("utf-8-sig"), filename
        except UnicodeDecodeError as error:
            raise APIError(400, "TEXT_PARSE_ERROR", "We couldn't read this text file. Please save it as UTF-8 or paste your resume.") from error

    try:
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages), filename
    except Exception as error:
        raise APIError(400, "PDF_PARSE_ERROR", "We couldn't read this PDF. Try another file or paste the resume text instead.") from error


def validate_resume_text(text: str) -> str:
    normalized = "\n".join(line.rstrip() for line in text.replace("\x00", "").splitlines()).strip()
    if len(normalized) < 40 or not any(character.isalpha() for character in normalized):
        raise APIError(400, "EMPTY_RESUME", "We couldn't find any resume content. Please upload another file or paste your resume.")
    if len(normalized) > settings.max_resume_characters:
        raise APIError(413, "RESUME_TOO_LONG", "This resume is too long to analyze. Please shorten it and try again.")
    return normalized

