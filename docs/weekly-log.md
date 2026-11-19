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

## Week 2 — Prompting, tier limits, CLI prototype

**Done**

- `app/services/tiers.py`: per-tier limits (pages, questions, prompt lines) checked
  before any API call; 27 boundary tests with `pytest.mark.parametrize`
- `app/services/generator.py`: PDF + prompt → complete `exam`-class LaTeX via Claude
  (streaming); prompt v1 → v2 (max 3 parts per question, `<user_instructions>` tags)
- Prompt-injection defense in 3 layers (code limits, tag stripping, system-prompt rule);
  unit tests for the tag stripping, incl. an attack found while writing the tests
  (removing a tag can create a new tag → repeat until nothing changes)
- `quiz.py` CLI (`argparse`): exit codes, errors on stderr, no tracebacks for
  expected failures; all 3 samples generate 5 questions that compile in Overleaf
- Every run logged with tokens and cost (`docs/prompt-log.md`)

**Keep**

- Learning error handling: which exceptions to catch, where, and how to turn them
  into clear messages and exit codes.
- Parametrized tests (`pytest.param` with ids) for many cases in one test.

**Problem**

- New libraries (argparse, pypdf, anthropic SDK) and `sys` (argv, stdout/stderr,
  exit codes) were unfamiliar — but learning them was worth it.

**Try**

- Keep the TODO → review format, but make TODOs harder: give only the function name,
  what it must do and return, and which existing functions to use — no step-by-step hints.

**Prompt v1/v2: problems and improvements** (input for week 3)

| Problem | Seen in | Fix |
|---|---|---|
| "Question" was ambiguous: N = 5 gave 17 sub-parts | v1, run 1 | v2: max 3 parts. Week 3: enforce in the JSON schema |
| Rules (N, max parts) are only *asked for* in the prompt | all runs | Week 3: validate the structured output in code; reject/retry |
| Claude tends to use the maximum number of parts | v2 runs | Watch it; add guidance if quizzes feel too long |
| Output is free-form LaTeX, so we can't check answers or reformat | all runs | Week 3: JSON (type, body, choices, answer, solution, difficulty) + our own template |
| "Compiles" is checked by hand in Overleaf | all runs | Week 3: local compile check + automatic fix-and-retry loop |
| Cost grows with pages (12 pages ≈ 2× a 5-page PDF) | CLI runs | Keep page limits per tier; revisit prices with real numbers |
| Injection defense tested once per attack | runs 2–3 | Week 4 eval set: repeat attacks, measure the rate |
