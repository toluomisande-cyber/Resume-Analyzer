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
    junior: int = Field(ge=0, le=100)
    mid: int = Field(ge=0, le=100)
    senior: int = Field(ge=0, le=100)


class SkillsAnalysis(BaseModel):
    detected: list[str] = Field(default_factory=list)
    recommended: list[str] = Field(default_factory=list)


class ProjectRecommendation(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str = Field(min_length=1, max_length=500)
    skills: list[str] = Field(default_factory=list)


class ExperienceInsight(BaseModel):
    current: str = Field(min_length=1, max_length=600)
    assessment: str = Field(min_length=1, max_length=500)
    suggestion: str = Field(min_length=1, max_length=600)


class ExperienceAnalysis(BaseModel):
    overview: str = Field(default="No work experience section was detected.", max_length=700)
    strong_points: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    bullet_insights: list[ExperienceInsight] = Field(default_factory=list)


class EducationAnalysis(BaseModel):
    overview: str = Field(default="Education details were not clearly detected.", max_length=700)
    relevance: str = Field(default="Add relevant coursework, certifications, or training where appropriate.", max_length=500)
    recommendations: list[str] = Field(default_factory=list)


class ATSAnalysis(BaseModel):
    overview: str = Field(min_length=1, max_length=700)
    section_headings: list[str] = Field(default_factory=list)
    keyword_alignment: str = Field(min_length=1, max_length=500)
    readability: str = Field(min_length=1, max_length=500)
    parsing_notes: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    career_field: str = Field(min_length=1, max_length=120)
    scores: Scores
    summary: str = Field(min_length=1, max_length=900)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    skills: SkillsAnalysis = Field(default_factory=SkillsAnalysis)
    projects: list[ProjectRecommendation] = Field(default_factory=list)
    experience: ExperienceAnalysis = Field(default_factory=ExperienceAnalysis)
    education: EducationAnalysis = Field(default_factory=EducationAnalysis)
    ats_analysis: ATSAnalysis

    @field_validator("strengths", "improvements", mode="before")
    @classmethod
    def keep_string_lists(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]


class SuccessResponse(BaseModel):
    success: bool = True
    data: ResumeAnalysis

