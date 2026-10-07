import json
import logging
import re

import httpx

from app.config import settings
from app.models.schemas import ResumeAnalysis
from app.utils.errors import APIError

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a meticulous resume reviewer. Analyze only the information in the resume. "
    "Never invent employers, accomplishments, dates, metrics, certifications, or skills. "
    "When evidence is absent, make a recommendation and explicitly frame it as not detected in the resume. "
    "Compare the candidate to the selected career field at junior, mid-level, and senior expectations. "
    "Scores are reasoned estimates as whole numbers between 0 and 100 (e.g. junior: 45, mid: 70, senior: 85), not employment guarantees or official ATS scores. "
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


def clean_and_parse_json(content: str) -> dict:
    if not content or not content.strip():
        raise ValueError("Empty response from AI")

    text = content.strip()

    # 1. Direct parse attempt
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass

    # 2. Extract content from markdown code fence
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence_match:
        snippet = fence_match.group(1).strip()
        try:
            return json.loads(snippet, strict=False)
        except json.JSONDecodeError:
            text = snippet

    # 3. Locate outer JSON boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError:
            pass

        # 4. Strip trailing commas before closing braces/brackets
        no_trailing_commas = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            return json.loads(no_trailing_commas, strict=False)
        except json.JSONDecodeError:
            pass

    # 5. Handle partially truncated JSON (repair open strings and brackets)
    if start != -1:
        truncated = text[start:].strip()
        truncated = re.sub(r",\s*$", "", truncated)
        open_quotes = truncated.count('"') - truncated.count('\\"')
        if open_quotes % 2 != 0:
            truncated += '"'
        open_curlies = truncated.count("{") - truncated.count("}")
        open_squares = truncated.count("[") - truncated.count("]")
        truncated += ("]" * max(0, open_squares)) + ("}" * max(0, open_curlies))
        truncated = re.sub(r",\s*([}\]])", r"\1", truncated)
        try:
            return json.loads(truncated, strict=False)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse valid JSON from AI response: {text[:200]}")


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
        "max_tokens": settings.openrouter_max_tokens,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    except httpx.TimeoutException as error:
        logger.error(f"AI request timed out: {error}")
        raise APIError(504, "AI_TIMEOUT", "The analysis took too long. Please try again.") from error
    except httpx.RequestError as error:
        logger.error(f"AI connection error: {error}")
        raise APIError(503, "AI_UNAVAILABLE", "We couldn't connect to the AI service right now. Please try again in a moment.") from error

    if response.status_code == 429:
        logger.warning("OpenRouter rate limit reached (429)")
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
        logger.error(f"OpenRouter returned status {response.status_code}: {error_msg}")
        raise APIError(503, "AI_UNAVAILABLE", error_msg)

    try:
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            err = data["error"]
            err_msg = err.get("message", "AI provider returned an error") if isinstance(err, dict) else str(err)
            logger.error(f"OpenRouter response contained error object: {err_msg}")
            raise APIError(503, "AI_UNAVAILABLE", err_msg)

        choice = data["choices"][0]["message"]["content"]
        content = choice if isinstance(choice, str) else "".join(item.get("text", "") for item in choice)
        parsed_data = clean_and_parse_json(content)
        analysis = ResumeAnalysis.model_validate(parsed_data)
    except APIError:
        raise
    except Exception as error:
        logger.error(f"Failed to parse or validate AI response: {error}", exc_info=True)
        # Log snippet of response if available
        try:
            raw_preview = content[:500] if "content" in locals() else response.text[:500]
            logger.error(f"Raw AI content preview: {raw_preview}")
        except Exception:
            pass
        raise APIError(502, "AI_RESPONSE_INVALID", "The AI returned an unreadable analysis. Please try again.") from error

    return analysis.model_copy(update={"career_field": career})
