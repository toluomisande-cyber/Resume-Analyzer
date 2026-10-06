import type { APIResponse, ResumeAnalysis } from "@/types/analysis";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function requestAnalysis(input: { file: File | null; text: string; career: string; }): Promise<ResumeAnalysis> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 120_000);
  try {
    const body = input.file
      ? (() => { const form = new FormData(); form.append("file", input.file); form.append("career_field", input.career); return form; })()
      : JSON.stringify({ resume_content: input.text, career_field: input.career });
    const response = await fetch(`${API_URL}/api/analyze`, { method: "POST", body, headers: input.file ? undefined : { "Content-Type": "application/json" }, signal: controller.signal });
    const payload = await response.json().catch(() => null) as APIResponse | null;
    if (!payload || !payload.success) throw new Error(payload && !payload.success ? payload.error.message : "We couldn't analyze your resume. Please try again.");
    return payload.data;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw new Error("The analysis took too long. Please try again.");
    if (error instanceof TypeError) throw new Error("We couldn't reach the analysis service. Check that the backend is running, then try again.");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

