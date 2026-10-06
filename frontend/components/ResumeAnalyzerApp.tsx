"use client";

import { ArrowRight, Brain, CheckCircle, Lightning, ShieldCheck } from "@phosphor-icons/react";
import { useState } from "react";
import { requestAnalysis } from "@/lib/api";
import type { ResumeAnalysis } from "@/types/analysis";
import { AnalysisSkeleton } from "./AnalysisSkeleton";
import { CareerSelect } from "./CareerSelect";
import { ResultsDashboard } from "./ResultsDashboard";
import { ResumeInput } from "./ResumeInput";

type Screen = "form" | "loading" | "results";

export function ResumeAnalyzerApp() {
  const [screen, setScreen] = useState<Screen>("form");
  const [mode, setMode] = useState<"upload" | "paste">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [career, setCareer] = useState("");
  const [customCareer, setCustomCareer] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const effectiveCareer = career === "Other" ? customCareer.trim() : career;
  const hasResume = mode === "upload" ? Boolean(file) : text.trim().length >= 40;
  const canAnalyze = hasResume && Boolean(effectiveCareer);

  const analyze = async () => {
    if (!hasResume) return setError("Add a PDF, TXT file, or pasted resume before analyzing.");
    if (!effectiveCareer) return setError("Choose a career field before analyzing your resume.");
    setError(null);
    setScreen("loading");
    try {
      const data = await requestAnalysis({
        file: mode === "upload" ? file : null,
        text,
        career: effectiveCareer,
      });
      setAnalysis(data);
      setScreen("results");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (requestError) {
      console.error("Resume analysis error:", requestError);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "We couldn't analyze your resume. Please try again."
      );
      setScreen("form");
      setTimeout(
        () =>
          document
            .getElementById("analyzer")
            ?.scrollIntoView({ behavior: "smooth", block: "start" }),
        0
      );
    }
  };
  const reset = () => { setScreen("form"); setFile(null); setText(""); setCareer(""); setCustomCareer(""); setError(null); setAnalysis(null); setTimeout(() => document.getElementById("analyzer")?.scrollIntoView({ behavior: "smooth", block: "start" }), 0); };
  if (screen === "loading") return <AnalysisSkeleton />;
  if (screen === "results" && analysis) return <ResultsDashboard analysis={analysis} onReset={reset} />;
  return <main><header className="site-header"><a href="#top" className="brand">Resume<span>Analyzer</span></a><a href="#analyzer" className="text-link">Start analysis <ArrowRight size={16} /></a></header><section id="top" className="hero"><div className="hero-copy"><p className="label">Career clarity, without the guesswork</p><h1>Know how strong your resume really is.</h1><p>Upload your resume, choose your career path, and get an AI-powered review with practical next steps.</p><button type="button" className="button primary" onClick={() => document.getElementById("analyzer")?.scrollIntoView({ behavior: "smooth", block: "start" })}>Analyze my resume <ArrowRight size={19} weight="bold" /></button></div><div className="hero-visual" aria-label="Example resume analysis preview"><div className="preview-top"><span>Career fit</span><strong>Full Stack Developer</strong></div><div className="preview-score"><span>Mid-level</span><strong>68<small>/100</small></strong><i><b /></i></div><div className="preview-lines"><em /><em /><em /></div><div className="preview-signal"><CheckCircle size={20} weight="fill" /> Evidence-based recommendations</div></div></section><section className="value-strip" aria-label="Product benefits"><div><Brain size={23} weight="fill" /><span>Career-specific scoring</span></div><div><Lightning size={23} weight="fill" /><span>Actionable recommendations</span></div><div><ShieldCheck size={23} weight="fill" /><span>Private by design</span></div></section><section id="analyzer" className="analyzer-section"><div className="analyzer-intro"><p className="label">Start your review</p><h2>One focused analysis, built around your next move.</h2><p>Your resume is processed only for this request. Nothing is stored in this MVP.</p></div><div className="form-grid"><ResumeInput mode={mode} file={file} text={text} error={error} onModeChange={setMode} onFileChange={setFile} onTextChange={setText} onError={setError} /><CareerSelect value={career} customValue={customCareer} onChange={(value) => { setCareer(value); setError(null); }} onCustomChange={(value) => { setCustomCareer(value); setError(null); }} /></div><div className="analyze-bar"><p>{canAnalyze ? `Ready to review for ${effectiveCareer}.` : "Add your resume and select a target career to continue."}</p><button type="button" className="button primary" disabled={!canAnalyze} onClick={analyze}>Analyze resume <ArrowRight size={19} weight="bold" /></button></div></section></main>;
}
