# Resume Analyzer

Resume Analyzer is a focused full-stack MVP for career-specific AI resume reviews. It accepts a PDF, TXT file, or pasted resume text, then uses Gemini through OpenRouter to return structured scores, evidence-based feedback, skills guidance, project ideas, experience notes, and an ATS-style structure review.

## Features

- PDF and UTF-8 TXT upload with drag-and-drop support
- Pasted-resume alternative with client and server validation
- Searchable career selection with a custom `Other` field
- Three career-level scores: junior, mid-level, and senior
- Evidence-based strengths, improvements, skill recommendations, projects, education, experience, and ATS-style analysis
- Animated skeleton state, retryable errors, and a complete reset flow
- OpenRouter API key remains exclusively on the FastAPI backend
- No database and no permanent resume storage in this MVP

## Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, pypdf, httpx
- AI: Gemini model accessed through OpenRouter

## Project Structure

```text
Resume Analyzer/
  frontend/                 Next.js application
    app/                    Route and global styling
    components/             Input, loading, and dashboard components
    lib/                    API client and career data
    types/                  API response types
  backend/                  FastAPI application
    app/routes/             REST endpoints
    app/services/           PDF extraction and OpenRouter integration
    app/models/             Request and response validation
```

## Prerequisites

Install the following before running locally:

- Node.js 20 or newer
- Python 3.11 or newer
- An OpenRouter API key with access to a Gemini model

## Configure the Backend

Open one terminal:

```powershell
cd "Resume Analyzer\\backend"
py -3 -m venv .venv
\..venv\Scripts\Activate.ps1
pip install -r requirements.txts


Open `backend/.env` and set the following values:

```env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.5-flash
FRONTEND_URL=http://localhost:3000
```

Start the API:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

```

The health check is available at `http://localhost:8000/health`.

## Configure the Frontend

Open a second terminal:
y   
```powershell
cd "Resume Analyzer\\frontend"
npm install
Copy-Item .env.example .env.local
npm run dev
```

Copy-Item .env.example .env
```Open `http://localhost:3000`.

`NEXT_PUBLIC_API_URL` may be changed in `frontend/.env.local` when the API runs on another host or port. Never put the OpenRouter key in a `NEXT_PUBLIC_` variable.

## API

### `POST /api/analyze
`

Accepts either:

- `multipart/form-data` with `file` (PDF or TXT) and `career_field`
- JSON with `resume_content`, `career_field`, and optional `filename`
 
Success response:

```json
{
  "success": true,
  "data": {
    "career_field": "Full Stack Developer",
    "scores": { "junior": 82, "mid": 68, "senior": 51 }
  }
}
```

Failure response:

```json
{
  "success": false,
  "error": {
    "code": "PDF_PARSE_ERROR",
    "message": "We couldn't read this PDF. Try another file or paste the resume text instead."
  }
}
```

## Security and Privacy

- The API key is read only by the backend process.
- Files are limited to PDF/TXT and 5 MB.
- Uploaded files are parsed in memory and are not persisted.
- Resume contents and API credentials are not logged by the app.
- AI responses are parsed and validated before being returned to the browser.

## Troubleshooting

**`node`, `npm`, or `python` is not recognized**: install Node.js and Python, then reopen PowerShell so the PATH updates.

**The frontend cannot connect**: verify the FastAPI server is listening on port 8000 and that `NEXT_PUBLIC_API_URL` matches it.

**AI service is not configured**: create `backend/.env`, set `OPENROUTER_API_KEY`, and restart the backend.

**AI usage is temporarily unavailable**: check OpenRouter credits, model access, and quota, then retry.

**PDF cannot be read**: use a text-based PDF or paste the resume content. Image-only PDFs cannot always produce readable text.

## Future Improvements

- DOCX extraction
- Optional side-by-side resume rewrite workflow
- User-controlled export to PDF or Markdown
- Per-section confidence indicators
- Automated tests and CI
