# Quiz Generator

A web service that turns a PDF and a prompt into quiz questions with Claude, and returns them as **LaTeX that is verified to compile**.

> 🚧 Work in progress (8-week plan, week 1). Planned URL: https://quiz.mathware.dev

## Features (MVP goals)

- Sign up / log in, with per-tier usage limits (Free, Basic, Pro)
- Upload a PDF + prompt → generate N questions (multiple choice, short answer, free response)
- LaTeX output with automatic compile check (auto-fix and retry on failure)
- In-browser math preview, `.tex` / PDF download
- Accuracy measured on an evaluation set (compile success rate, answer accuracy)

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| LLM | Claude API (Anthropic) |
| Database | PostgreSQL (Neon) |
| Frontend | React + TypeScript (Vite), KaTeX |
| Infra | Docker, Cloudflare Pages, GitHub Actions |

## Project structure

```
app/            FastAPI application
app/services/   Core logic (PDF parsing, question generation, LaTeX compile, limit checks)
tests/          pytest tests
docs/           Design notes and evaluation results
samples/        Sample PDFs for local testing (not committed)
```

## Getting started

```bash
uv sync          # install dependencies into .venv
```

(More steps will be added as features land.)

## Results

Evaluation results will be recorded here in week 4 (baseline) and week 8 (after improvements).
