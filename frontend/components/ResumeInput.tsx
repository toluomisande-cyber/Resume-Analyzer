"use client";

import { FileArrowUp, FileText, Trash } from "@phosphor-icons/react";
import { ChangeEvent, DragEvent, useRef } from "react";

type ResumeInputProps = {
  mode: "upload" | "paste";
  file: File | null;
  text: string;
  error: string | null;
  onModeChange: (mode: "upload" | "paste") => void;
  onFileChange: (file: File | null) => void;
  onTextChange: (value: string) => void;
  onError: (message: string | null) => void;
};

const MAX_FILE_BYTES = 5 * 1024 * 1024;

export function ResumeInput({ mode, file, text, error, onModeChange, onFileChange, onTextChange, onError }: ResumeInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const choose = (selected: File | null) => {
    if (!selected) return;
    const allowed = selected.name.toLowerCase().endsWith(".pdf") || selected.name.toLowerCase().endsWith(".txt");
    if (!allowed) return onError("This file type isn't supported. Please upload a PDF or TXT file.");
    if (selected.size === 0) return onError("We couldn't find any resume content. Please upload another file or paste your resume.");
    if (selected.size > MAX_FILE_BYTES) return onError("This file is too large. Please upload a file smaller than 5 MB.");
    onError(null); onFileChange(selected);
  };
  const onInput = (event: ChangeEvent<HTMLInputElement>) => choose(event.target.files?.[0] ?? null);
  const onDrop = (event: DragEvent<HTMLDivElement>) => { event.preventDefault(); choose(event.dataTransfer.files?.[0] ?? null); };

  return <section aria-labelledby="resume-input-label" className="panel p-5 sm:p-7">
    <div className="mb-5 flex flex-wrap items-start justify-between gap-3"><div><p id="resume-input-label" className="label">Your resume</p><h2>Bring in the source material</h2></div><span className="hint">PDF or TXT, up to 5 MB</span></div>
    <div className="segmented" role="tablist" aria-label="Resume input method"><button type="button" role="tab" aria-selected={mode === "upload"} className={mode === "upload" ? "active" : ""} onClick={() => onModeChange("upload")}><FileArrowUp size={18} weight="bold" /> Upload resume</button><button type="button" role="tab" aria-selected={mode === "paste"} className={mode === "paste" ? "active" : ""} onClick={() => onModeChange("paste")}><FileText size={18} weight="bold" /> Paste resume</button></div>
    {mode === "upload" ? <div className="mt-5">
      <div className="dropzone" onDragOver={(event) => event.preventDefault()} onDrop={onDrop} onClick={() => inputRef.current?.click()} role="button" tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") inputRef.current?.click(); }} aria-label="Upload a PDF or TXT resume">
        <span className="icon-chip"><FileArrowUp size={26} weight="bold" /></span><div><strong>Drop your resume here</strong><p>or select a PDF or TXT file from your device</p></div><button type="button" className="button secondary" onClick={(event) => { event.stopPropagation(); inputRef.current?.click(); }}>Choose file</button>
      </div>
      <input ref={inputRef} type="file" accept=".pdf,.txt,application/pdf,text/plain" className="sr-only" onChange={onInput} />
      {file && <div className="selected-file"><FileText size={20} weight="fill" /><span><strong>{file.name}</strong><small>{Math.max(1, Math.round(file.size / 1024))} KB ready to analyze</small></span><button type="button" className="icon-button" aria-label="Remove selected file" title="Remove selected file" onClick={() => { onFileChange(null); onError(null); if (inputRef.current) inputRef.current.value = ""; }}><Trash size={18} /></button></div>}
    </div> : <div className="mt-5"><label className="sr-only" htmlFor="resume-content">Resume content</label><textarea id="resume-content" className="textarea" value={text} onChange={(event) => { onTextChange(event.target.value); onError(null); }} placeholder="Paste your resume content here..." /><p className="hint mt-2">Include experience, education, projects, skills, and achievements for a more useful review.</p></div>}
    {error && <p className="form-error" role="alert">{error}</p>}
  </section>;
}

