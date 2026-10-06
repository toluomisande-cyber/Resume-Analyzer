"use client";

import { CaretDown, MagnifyingGlass } from "@phosphor-icons/react";
import { useMemo, useState } from "react";
import { CAREER_FIELDS } from "@/lib/careers";

type CareerSelectProps = { value: string; customValue: string; onChange: (value: string) => void; onCustomChange: (value: string) => void; };

export function CareerSelect({ value, customValue, onChange, onCustomChange }: CareerSelectProps) {
  const [query, setQuery] = useState("");
  const visibleFields = useMemo(() => CAREER_FIELDS.filter((career) => career.toLowerCase().includes(query.toLowerCase())), [query]);
  return <section aria-labelledby="career-label" className="panel p-5 sm:p-7"><div className="mb-5"><p id="career-label" className="label">Target career</p><h2>Choose the role you are aiming for</h2><p className="panel-copy">The analysis uses this context to score experience, skills, and next steps at each career level.</p></div><label className="search-field"><MagnifyingGlass size={19} /><span className="sr-only">Search career fields</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search career fields" /></label><div className="career-list" role="listbox" aria-label="Career fields">{visibleFields.map((career) => <button key={career} type="button" role="option" aria-selected={value === career} className={value === career ? "career-option selected" : "career-option"} onClick={() => onChange(career)}>{career}{value === career && <CaretDown size={18} weight="bold" />}</button>)}</div>{value === "Other" && <div className="custom-career"><label htmlFor="custom-career">Enter your career field</label><input id="custom-career" value={customValue} onChange={(event) => onCustomChange(event.target.value)} placeholder="For example, Technical Writer" /></div>}</section>;
}

