import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


class APIErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: APIErrorBody


class ResumeTextRequest(BaseModel):
    resume_content: str = Field(min_length=1, max_length=100_000)
    career_field: str = Field(min_length=1, max_length=120)
    filename: str | None = Field(default=None, max_length=255)


class Scores(BaseModel):
    junior: int = Field(default=50, ge=0, le=100)
    mid: int = Field(default=50, ge=0, le=100)
    senior: int = Field(default=50, ge=0, le=100)

    @field_validator("junior", "mid", "senior", mode="before")
    @classmethod
    def sanitize_score(cls, value: Any) -> int:
        num = None
        if isinstance(value, (int, float)):
            num = float(value)
        elif isinstance(value, str):
            clean = re.sub(r"[^\d.]", "", value)
            if clean:
                try:
                    num = float(clean)
                except ValueError:
                    pass
        if num is not None:
            if 0 < num <= 10:
                num = num * 10
            return max(0, min(100, int(round(num))))
        return 50


class SkillsAnalysis(BaseModel):
    detected: list[str] = Field(default_factory=list)
    recommended: list[str] = Field(default_factory=list)

    @field_validator("detected", "recommended", mode="before")
    @classmethod
    def sanitize_skills(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [s.strip() for s in value.split(",") if s.strip()]
        return []


class ProjectRecommendation(BaseModel):
    title: str = Field(default="Recommended Project")
    description: str = Field(default="")
    skills: list[str] = Field(default_factory=list)

    @field_validator("title", "description", mode="before")
    @classmethod
    def sanitize_str(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("skills", mode="before")
    @classmethod
    def sanitize_skills(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(s).strip() for s in value if str(s).strip()]
        if isinstance(value, str) and value.strip():
            return [s.strip() for s in value.split(",") if s.strip()]
        return []


class ExperienceInsight(BaseModel):
    current: str = Field(default="")
    assessment: str = Field(default="")
    suggestion: str = Field(default="")

    @field_validator("current", "assessment", "suggestion", mode="before")
    @classmethod
    def sanitize_str(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""


class ExperienceAnalysis(BaseModel):
    overview: str = Field(default="No work experience section was detected.")
    strong_points: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    bullet_insights: list[ExperienceInsight] = Field(default_factory=list)

    @field_validator("overview", mode="before")
    @classmethod
    def sanitize_overview(cls, value: Any) -> str:
        return str(value).strip() if value is not None else "No work experience section was detected."

    @field_validator("strong_points", "weak_points", "suggestions", mode="before")
    @classmethod
    def sanitize_string_list(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    @field_validator("bullet_insights", mode="before")
    @classmethod
    def sanitize_bullet_insights(cls, value: Any) -> list[Any]:
        if not isinstance(value, list):
            return []
        cleaned = []
        for item in value:
            if isinstance(item, dict):
                cleaned.append(item)
            elif isinstance(item, str) and item.strip():
                cleaned.append({
                    "current": item.strip(),
                    "assessment": "Needs optimization for impact and clarity.",
                    "suggestion": "Quantify outcomes with measurable metrics."
                })
        return cleaned


class EducationAnalysis(BaseModel):
    overview: str = Field(default="Education details were not clearly detected.")
    relevance: str = Field(default="Add relevant coursework, certifications, or training where appropriate.")
    recommendations: list[str] = Field(default_factory=list)

    @field_validator("overview", "relevance", mode="before")
    @classmethod
    def sanitize_str(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("recommendations", mode="before")
    @classmethod
    def sanitize_recommendations(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []


class ATSAnalysis(BaseModel):
    overview: str = Field(default="ATS evaluation complete.")
    section_headings: list[str] = Field(default_factory=list)
    keyword_alignment: str = Field(default="")
    readability: str = Field(default="")
    parsing_notes: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    @field_validator("overview", "keyword_alignment", "readability", mode="before")
    @classmethod
    def sanitize_str(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("section_headings", "parsing_notes", "recommendations", mode="before")
    @classmethod
    def sanitize_string_list(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []


class ResumeAnalysis(BaseModel):
    career_field: str = Field(default="")
    scores: Scores = Field(default_factory=Scores)
    summary: str = Field(default="")
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    skills: SkillsAnalysis = Field(default_factory=SkillsAnalysis)
    projects: list[ProjectRecommendation] = Field(default_factory=list)
    experience: ExperienceAnalysis = Field(default_factory=ExperienceAnalysis)
    education: EducationAnalysis = Field(default_factory=EducationAnalysis)
    ats_analysis: ATSAnalysis = Field(default_factory=ATSAnalysis)

    @field_validator("skills", "experience", "education", "ats_analysis", "scores", mode="before")
    @classmethod
    def sanitize_dict_fields(cls, value: Any) -> Any:
        if value is None or not isinstance(value, dict):
            return {}
        return value

    @field_validator("career_field", "summary", mode="before")
    @classmethod
    def sanitize_str(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("strengths", "improvements", mode="before")
    @classmethod
    def sanitize_string_list(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []


class SuccessResponse(BaseModel):
    success: bool = True
    data: ResumeAnalysis
