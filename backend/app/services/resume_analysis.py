import json
import re

import httpx

from app.config import settings
from app.models.schemas import ResumeAnalysis
from app.utils.errors import APIError


SYSTEM_PROMPT = (
    "You are a meticulous resume reviewer. Analyze only the information in the resume. "
    "Never invent employers, accomplishments, dates, metrics, certifications, or skills. "
    "When evidence is absent, make a recommendation and explicitly frame it as not detected in the resume. "
    "Compare the candidate to the selected career field at junior, mid-level, and senior expectations. "
    "Scores are reasoned estimates, not employment guarantees or official ATS scores. "
    "Be thorough, concrete, and concise (1-2 clear sentences per bullet or description). "
    "Return JSON only and adhere exactly to the requested schema."
)


def build_user_prompt(resume: str, career: str) -> str:
    schema = """{
  \"career_field\": \"target career\",
  \"scores\": {\"junior\": 0, \"mid\": 0, \"senior\": 0},
  \"summary\": \"concise, evidence-based overall assessment\",
  \"strengths\": [\"supported strength\"],
  \"improvements\": [\"specific career-targeted improvement\"],
  \"skills\": {\"detected\": [\"skill explicitly present\"], \"recommended\": [\"relevant skill not detected in the resume\"]},
  \"projects\": [{\"title\": \"realistic project\", \"description\": \"why it fits candidate\", \"skills\": [\"skill\"]}],
  \"experience\": {\"overview\": \"evidence-based overview\", \"strong_points\": [\"supported point\"], \"weak_points\": [\"gap or unclear area\"], \"suggestions\": [\"actionable suggestion\"], \"bullet_insights\": [{\"current\": \"quoted bullet\", \"assessment\": \"evaluation\", \"suggestion\": \"rewrite guidance\"}]},
  \"education\": {\"overview\": \"evidence-based\", \"relevance\": \"relevance to target career\", \"recommendations\": [\"actionable recommendation\"]},
  \"ats_analysis\": {\"overview\": \"ATS-style observation\", \"section_headings\": [\"observation\"], \"keyword_alignment\": \"evidence-based\", \"readability\": \"evidence-based\", \"parsing_notes\": [\"observation\"], \"recommendations\": [\"actionable recommendation\"]}
}"""
    return f"Target career: {career}\n\nReturn one JSON object with this exact shape:\n{schema}\n\nResume:\n---\n{resume}\n---"


def _extract_json(content: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise APIError(502, "AI_RESPONSE_INVALID", "The AI returned an unreadable analysis. Please try again.")
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as error:
            raise APIError(502, "AI_RESPONSE_INVALID", "The AI returned an unreadable analysis. Please try again.") from error


async def analyze_resume(resume: str, career: str) -> ResumeAnalysis:
    if not settings.openrouter_api_key:
        raise APIError(503, "AI_CONFIGURATION_ERROR", "AI service is not configured. Add OPENROUTER_API_KEY to backend/.env and restart the API.")

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(resume, career)}
        ],
        "temperature": 0.2,
        "max_tokens": 2500,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    except httpx.TimeoutException as error:
        raise APIError(504, "AI_TIMEOUT", "The analysis took too long. Please try again.") from error
    except httpx.RequestError as error:
        raise APIError(503, "AI_UNAVAILABLE", "We couldn't connect to the AI service right now. Please try again in a moment.") from error

    if response.status_code == 429:
        raise APIError(429, "AI_USAGE_UNAVAILABLE", "Model rate limit reached. Please wait a moment and try again.")
    if response.status_code >= 400:
        error_msg = "We couldn't connect to the AI service right now. Please try again in a moment."
        try:
            err_json = response.json()
            if isinstance(err_json, dict) and "error" in err_json:
                api_err = err_json["error"]
                if isinstance(api_err, dict) and "message" in api_err:
                    error_msg = api_err["message"]
                elif isinstance(api_err, str):
                    error_msg = api_err
        except Exception:
            pass
        raise APIError(503, "AI_UNAVAILABLE", error_msg)
    try:
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            err = data["error"]
            err_msg = err.get("message", "AI provider returned an error") if isinstance(err, dict) else str(err)
            raise APIError(503, "AI_UNAVAILABLE", err_msg)
        choice = data["choices"][0]["message"]["content"]
        content = choice if isinstance(choice, str) else "".join(item.get("text", "") for item in choice)
        analysis = ResumeAnalysis.model_validate(_extract_json(content))
    except APIError:
        raise
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise APIError(502, "AI_RESPONSE_INVALID", "The AI returned an unreadable analysis. Please try again.") from error
    return analysis.model_copy(update={"career_field": career})

