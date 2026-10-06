export interface Scores { junior: number; mid: number; senior: number; }
export interface SkillsAnalysis { detected: string[]; recommended: string[]; }
export interface ProjectRecommendation { title: string; description: string; skills: string[]; }
export interface ExperienceInsight { current: string; assessment: string; suggestion: string; }
export interface ExperienceAnalysis { overview: string; strong_points: string[]; weak_points: string[]; suggestions: string[]; bullet_insights: ExperienceInsight[]; }
export interface EducationAnalysis { overview: string; relevance: string; recommendations: string[]; }
export interface ATSAnalysis { overview: string; section_headings: string[]; keyword_alignment: string; readability: string; parsing_notes: string[]; recommendations: string[]; }
export interface ResumeAnalysis { career_field: string; scores: Scores; summary: string; strengths: string[]; improvements: string[]; skills: SkillsAnalysis; projects: ProjectRecommendation[]; experience: ExperienceAnalysis; education: EducationAnalysis; ats_analysis: ATSAnalysis; }
export interface APIError { code: string; message: string; }
export type APIResponse = { success: true; data: ResumeAnalysis } | { success: false; error: APIError };

