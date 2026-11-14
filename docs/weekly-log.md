# Weekly Log

Short retrospectives at the end of each week (Keep / Problem / Try).

## Week 1 — Environment, first Claude call, PDF parsing

**Done**

- Project setup with `uv` (Python 3.12), Git, and a public GitHub repo
- FastAPI app with a `/health` endpoint and a pytest test
- Configuration via `pydantic-settings`; API key kept in a git-ignored `.env` (`SecretStr`)
- First Claude API call (`scripts/hello_claude.py`)
- Compared pypdf text extraction vs. sending the PDF directly to Claude on 3 samples,
  graded 21 formulas by hand (pypdf 10%, Claude 100%) → decision: send PDFs directly
  to Claude (`docs/parsing-notes.md`)

**Keep**

- The local commit → GitHub push workflow now feels natural.
- Separating secrets into `.env` and loading them through a settings object,
  and actually using it in working code.

**Problem**

- Writing the implementation code myself is still unfamiliar in places.
- Git beyond the basics is unclear — especially how to undo changes
  (never tried it, so not sure what happens when you do).

**Try**

- Practice undoing in Git (`restore`, `revert`, `reset`) in a throwaway repo
  before week 2, so mistakes in the real project are not scary.
- Keep the current format: TODOs in files, review, learning points.
