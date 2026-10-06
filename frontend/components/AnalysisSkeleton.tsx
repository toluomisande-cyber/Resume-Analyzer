"use client";

import { useEffect, useState } from "react";

const STATUSES = ["Reading resume", "Identifying experience", "Evaluating skills", "Comparing career requirements", "Generating recommendations"];

export function AnalysisSkeleton() {
  const [statusIndex, setStatusIndex] = useState(0);
  useEffect(() => { const interval = window.setInterval(() => setStatusIndex((current) => Math.min(current + 1, STATUSES.length - 1)), 1800); return () => window.clearInterval(interval); }, []);
  return <main className="analysis-wrap" aria-live="polite"><section className="loading-header"><p className="label">Analysis in progress</p><h1>Making your resume useful.</h1><p>{STATUSES[statusIndex]}</p></section><div className="skeleton-grid"><div className="skeleton-card tall"><i /><i /><i /></div><div className="skeleton-card"><i /><i /></div><div className="skeleton-card"><i /><i /></div><div className="skeleton-card wide"><i /><i /><i /><i /></div></div></main>;
}
