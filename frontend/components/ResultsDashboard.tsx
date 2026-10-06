"use client";

import {
  ArrowCounterClockwise,
  ArrowRight,
  Briefcase,
  CheckCircle,
  FileText,
  GraduationCap,
  Lightbulb,
  MagnifyingGlass,
  ShieldCheck,
  Sparkle,
  ChartLineUp,
  Info,
} from "@phosphor-icons/react";
import type { ReactNode } from "react";
import type { ResumeAnalysis } from "@/types/analysis";

type ResultsDashboardProps = {
  analysis: ResumeAnalysis;
  onReset: () => void;
};

const scoreMeta = [
  { key: "junior", label: "Junior", detail: "Entry-level readiness" },
  { key: "mid", label: "Mid-level", detail: "Independent contribution" },
  { key: "senior", label: "Senior", detail: "Leadership and depth" },
] as const;

function Section({
  id,
  icon,
  title,
  children,
}: {
  id: string;
  icon: ReactNode;
  title: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="result-section">
      <div className="section-heading">
        <span className="icon-chip">{icon}</span>
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function List({
  items = [],
  tone = "positive",
}: {
  items?: string[];
  tone?: "positive" | "neutral";
}) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <ul className={`insight-list ${tone}`}>
      {safeItems.map((item, index) => (
        <li key={`${item}-${index}`}>
          <CheckCircle size={19} weight="fill" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function ResultsDashboard({ analysis, onReset }: ResultsDashboardProps) {
  const scores = analysis?.scores ?? { junior: 0, mid: 0, senior: 0 };
  const strengths = Array.isArray(analysis?.strengths) ? analysis.strengths : [];
  const improvements = Array.isArray(analysis?.improvements) ? analysis.improvements : [];
  const detectedSkills = Array.isArray(analysis?.skills?.detected) ? analysis.skills.detected : [];
  const recommendedSkills = Array.isArray(analysis?.skills?.recommended) ? analysis.skills.recommended : [];
  const projects = Array.isArray(analysis?.projects) ? analysis.projects : [];
  const experience = analysis?.experience ?? {
    overview: "",
    strong_points: [],
    weak_points: [],
    suggestions: [],
    bullet_insights: [],
  };
  const bulletInsights = Array.isArray(experience.bullet_insights) ? experience.bullet_insights : [];
  const education = analysis?.education ?? {
    overview: "",
    relevance: "",
    recommendations: [],
  };
  const ats = analysis?.ats_analysis ?? {
    overview: "",
    section_headings: [],
    keyword_alignment: "",
    readability: "",
    parsing_notes: [],
    recommendations: [],
  };

  return (
    <main className="results-wrap">
      <header className="results-header">
        <div>
          <p className="label">Resume analysis</p>
          <h1>Where you stand, and what to do next.</h1>
          <p className="results-career">
            <Briefcase size={18} weight="fill" /> Target career:{" "}
            <strong>{analysis?.career_field ?? "General"}</strong>
          </p>
        </div>
        <button type="button" className="button secondary" onClick={onReset}>
          <ArrowCounterClockwise size={18} weight="bold" /> Analyze another resume
        </button>
      </header>

      <section className="score-grid" aria-label="Career level scores">
        {scoreMeta.map(({ key, label, detail }) => {
          const scoreVal = typeof scores[key] === "number" ? scores[key] : 0;
          return (
            <article key={key} className="score-card">
              <div>
                <p>{label}</p>
                <span>{detail}</span>
              </div>
              <strong>
                {scoreVal}
                <small>/100</small>
              </strong>
              <div
                className="score-line"
                aria-label={`${label} score: ${scoreVal} out of 100`}
              >
                <i style={{ width: `${Math.min(100, Math.max(0, scoreVal))}%` }} />
              </div>
            </article>
          );
        })}
      </section>

      <nav className="result-nav" aria-label="Analysis sections">
        <a href="#overview">Overview</a>
        <a href="#skills">Skills</a>
        <a href="#projects">Projects</a>
        <a href="#experience">Experience</a>
        <a href="#ats">ATS-style analysis</a>
      </nav>

      <div className="result-layout">
        <div className="result-column">
          <Section
            id="overview"
            icon={<Sparkle size={21} weight="fill" />}
            title="Overall assessment"
          >
            <p className="summary-copy">{analysis?.summary ?? "No summary provided."}</p>
            <p className="disclaimer">
              AI-generated estimates, not a guarantee of employment or an official ATS score.
            </p>
          </Section>

          <Section
            id="strengths"
            icon={<ChartLineUp size={21} weight="bold" />}
            title="Strengths"
          >
            {strengths.length ? (
              <List items={strengths} />
            ) : (
              <p className="empty-copy">No clear strengths were detected from the submitted resume.</p>
            )}
          </Section>

          <Section
            id="improvements"
            icon={<Lightbulb size={21} weight="fill" />}
            title="Areas to improve"
          >
            {improvements.length ? (
              <ol className="numbered-list">
                {improvements.map((item, index) => (
                  <li key={`${item}-${index}`}>
                    <b>{String(index + 1).padStart(2, "0")}</b>
                    <span>{item}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="empty-copy">The analysis did not return improvement suggestions.</p>
            )}
          </Section>
        </div>

        <div className="result-column">
          <Section
            id="skills"
            icon={<MagnifyingGlass size={21} weight="bold" />}
            title="Skill analysis"
          >
            <div className="skills-block">
              <h3>Detected in the resume</h3>
              <div className="tag-list">
                {detectedSkills.length ? (
                  detectedSkills.map((skill) => <span key={skill}>{skill}</span>)
                ) : (
                  <p className="empty-copy">No skills were confidently detected.</p>
                )}
              </div>
            </div>
            <div className="skills-block">
              <h3>Recommended for this path</h3>
              <p className="subtle-copy">
                Not detected in the resume. Add only skills you can demonstrate.
              </p>
              <div className="tag-list recommendation">
                {recommendedSkills.map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
            </div>
          </Section>

          <Section
            id="education"
            icon={<GraduationCap size={21} weight="fill" />}
            title="Education"
          >
            <p className="section-copy">{education.overview || "No education details detected."}</p>
            {education.relevance && (
              <p className="section-copy strong-copy">{education.relevance}</p>
            )}
            {Array.isArray(education.recommendations) && education.recommendations.length > 0 && (
              <List items={education.recommendations} tone="neutral" />
            )}
          </Section>
        </div>
      </div>

      <Section
        id="projects"
        icon={<FileText size={21} weight="fill" />}
        title="Recommended projects"
      >
        <div className="project-list">
          {projects.map((project, index) => {
            const projectSkills = Array.isArray(project.skills) ? project.skills : [];
            return (
              <article key={`${project.title}-${index}`} className="project-item">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <h3>{project.title}</h3>
                  <p>{project.description}</p>
                  {projectSkills.length > 0 && (
                    <div className="tag-list">
                      {projectSkills.map((skill) => (
                        <em key={skill}>{skill}</em>
                      ))}
                    </div>
                  )}
                </div>
                <ArrowRight size={20} />
              </article>
            );
          })}
        </div>
      </Section>

      <div className="result-layout">
        <div className="result-column">
          <Section
            id="experience"
            icon={<Briefcase size={21} weight="fill" />}
            title="Experience analysis"
          >
            <p className="section-copy">{experience.overview || "No experience details detected."}</p>
            {Array.isArray(experience.strong_points) && experience.strong_points.length > 0 && (
              <List items={experience.strong_points} />
            )}
            {Array.isArray(experience.weak_points) && experience.weak_points.length > 0 && (
              <List items={experience.weak_points} tone="neutral" />
            )}
            {bulletInsights.map((item, index) => (
              <article className="bullet-insight" key={`${item.current}-${index}`}>
                <p>
                  <b>Current</b>
                  {item.current}
                </p>
                <p>
                  <b>Assessment</b>
                  {item.assessment}
                </p>
                <p>
                  <b>Suggestion</b>
                  {item.suggestion}
                </p>
              </article>
            ))}
          </Section>
        </div>

        <div className="result-column">
          <Section
            id="ats"
            icon={<ShieldCheck size={21} weight="fill" />}
            title="ATS & resume structure"
          >
            <p className="section-copy">{ats.overview || "No ATS overview provided."}</p>
            <div className="ats-notes">
              <p>
                <b>Keyword relevance</b>
                {ats.keyword_alignment}
              </p>
              <p>
                <b>Readability</b>
                {ats.readability}
              </p>
            </div>
            {Array.isArray(ats.recommendations) && ats.recommendations.length > 0 && (
              <List items={ats.recommendations} tone="neutral" />
            )}
          </Section>
        </div>
      </div>

      <footer className="results-footer">
        <Info size={19} /> This is an ATS-style analysis. It does not reproduce any company&#39;s exact screening system.
      </footer>
    </main>
  );
}
