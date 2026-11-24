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
    "Be thorough, concrete, and concise (1 clear sentence per bullet or description, max 3-4 items per list so the output is compact). "
    "Return raw valid JSON only (no markdown code fences) and adhere exactly to the requested schema."
)


def build_user_prompt(resume: str, career: str) -> str:
    schema = """{
  "career_field": "target career",
  "scores": {"junior": 0, "mid": 0, "senior": 0},
  "summary": "concise, evidence-based overall assessment",
  "strengths": ["supported strength"],
  "improvements": ["specific career-targeted improvement"],
  "skills": {"detected": ["skill explicitly present"], "recommended": ["relevant skill not detected in the resume"]},
  "projects": [{"title": "realistic project", "description": "why it fits candidate", "skills": ["skill"]}],
  "experience": {"overview": "evidence-based overview", "strong_points": ["supported point"], "weak_points": ["gap or unclear area"], "suggestions": ["actionable suggestion"], "bullet_insights": [{"current": "quoted bullet", "assessment": "evaluation", "suggestion": "rewrite guidance"}]},
  "education": {"overview": "evidence-based", "relevance": "relevance to target career", "recommendations": ["actionable recommendation"]},
  "ats_analysis": {"overview": "ATS-style observation", "section_headings": ["observation"], "keyword_alignment": "evidence-based", "readability": "evidence-based", "parsing_notes": ["observation"], "recommendations": ["actionable recommendation"]}
}"""
    return f"Target career: {career}\n\nReturn one JSON object with this exact shape:\n{schema}\n\nResume:\n---\n{resume}\n---"


def _repair_truncated_json(raw: str) -> dict | None:
    start = raw.find("{")
    if start == -1:
        return None
    s = raw[start:].strip()

    # Try progressively trimming from the end at safe structural boundaries
    for cut in range(len(s), max(2, len(s) - 600), -1):
        prefix = s[:cut].rstrip()
        if not prefix:
            break

        # Track open strings and brackets using a stack
        in_str = False
        esc = False
        stack: list[str] = []
        for ch in prefix:
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if not in_str:
                if ch == "{":
                    stack.append("}")
                elif ch == "[":
                    stack.append("]")
                elif ch in ("}", "]") and stack and stack[-1] == ch:
                    stack.pop()

        candidate = prefix
        if in_str:
            candidate += '"'
        candidate = re.sub(r"[,:\s]+$", "", candidate)
        # If it ends with a dangling object key like {..., "key" without a colon, fill ": null"
        if stack and stack[-1] == "}" and re.search(r'(?:[{,])\s*"[^"\\]*"$', candidate):
            candidate += ": null"
        elif re.search(r":\s*$", prefix):
            candidate += " null"

        candidate += "".join(reversed(stack))
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            parsed = json.loads(candidate, strict=False)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


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

    # 5. Stack-based repair for partially truncated JSON
    repaired = _repair_truncated_json(text)
    if repaired is not None:
        return repaired

    raise ValueError(f"Could not parse valid JSON from AI response: {text[:200]}")


async def analyze_resume(resume: str, career: str) -> ResumeAnalysis:
    if not settings.openrouter_api_key:
        raise APIError(503, "AI_CONFIGURATION_ERROR", "AI service is not configured. Add OPENROUTER_API_KEY to backend/.env and restart the API.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(resume, career)},
    ]

    # Prefer non-reasoning fast models first so max_tokens are never consumed by hidden thinking tokens
    configured = settings.openrouter_model.strip()
    if configured == "google/gemini-2.5-flash":
        candidate_models = ["google/gemini-2.5-flash-lite", "openai/gpt-4o-mini", "google/gemini-2.5-flash"]
    else:
        candidate_models = [configured, "google/gemini-2.5-flash-lite", "openai/gpt-4o-mini"]

    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    last_error: Exception | None = None
    last_response: httpx.Response | None = None

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
            for model_name in dict.fromkeys(candidate_models):
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": min(settings.openrouter_max_tokens, 2400),
                    "response_format": {"type": "json_object"},
                }
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                last_response = response

                if response.status_code in (400, 402) or "fewer max_tokens" in response.text or "can only afford" in response.text:
                    afford_match = re.search(r"can only afford\s+(\d+)", response.text)
                    if afford_match:
                        afforded = int(afford_match.group(1))
                        if afforded >= 1000:
                            retry_payload = {**payload, "max_tokens": afforded - 50}
                            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=retry_payload)
                            last_response = response

                if response.status_code >= 400:
                    logger.warning(f"Model {model_name} returned {response.status_code}, trying next candidate...")
                    continue

                try:
                    data = response.json()
                    if isinstance(data, dict) and "error" in data:
                        logger.warning(f"Model {model_name} returned error payload: {data['error']}")
                        continue

                    choice = data["choices"][0]["message"].get("content")
                    content = choice if isinstance(choice, str) else "".join(item.get("text", "") for item in (choice or []))
                    parsed_data = clean_and_parse_json(content)
                    analysis = ResumeAnalysis.model_validate(parsed_data)
                    return analysis.model_copy(update={"career_field": career})
                except Exception as parse_err:
                    last_error = parse_err
                    logger.warning(f"Model {model_name} output failed JSON parse/validation ({parse_err}), trying next candidate...")
                    continue
    except httpx.TimeoutException as error:
        logger.error(f"AI request timed out: {error}")
        raise APIError(504, "AI_TIMEOUT", "The analysis took too long. Please try again.") from error
    except httpx.RequestError as error:
        logger.error(f"AI connection error: {error}")
        raise APIError(503, "AI_UNAVAILABLE", "We couldn't connect to the AI service right now. Please try again in a moment.") from error

    if last_response is not None and last_response.status_code == 429:
        raise APIError(429, "AI_USAGE_UNAVAILABLE", "Model rate limit reached. Please wait a moment and try again.")

    if last_error is not None:
        logger.error(f"Failed to parse or validate AI response across candidates: {last_error}", exc_info=True)
        raise APIError(502, "AI_RESPONSE_INVALID", "The AI returned an unreadable analysis. Please try again.") from last_error

    raise APIError(503, "AI_UNAVAILABLE", "We couldn't connect to the AI service right now. Please try again in a moment.")
