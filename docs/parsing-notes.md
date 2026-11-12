# PDF Parsing Notes

Goal: decide how the app should read math-heavy PDFs before generating questions.
Two approaches are compared on the same samples:

- **A. Text extraction** with `pypdf` (`scripts/extract_text.py`)
- **B. Direct PDF input to Claude** (text + page images) — *week 1, Fri*

## Samples

Sample PDFs are kept local only (`samples/` is git-ignored) because some are copyrighted.

| ID | Source type | Pages | Producer |
|---|---|---|---|
| Sample1 | Course handout typeset in LaTeX (Poisson distribution) | 5 | LaTeX, re-saved via macOS Quartz |
| Sample2 | Commercial precalculus textbook excerpt (rational functions) | 12 | Publisher PDF, cropped in Preview |
| Sample3 | Calculus formula sheet written in Google Docs | 6 | Google Docs renderer (Skia) |

## A. Text extraction with pypdf (week 1, Thu)

| Sample | Characters extracted | Verdict |
|---|---|---|
| Sample1 | 6,463 | Prose OK, math structure lost, **symbols silently substituted** |
| Sample2 | ~25,000 | Prose mostly OK, **brackets/relations turned into digits/letters** |
| Sample3 | 1,153 | **Formulas missing entirely** |

### Failure case 1 — Sample1: structure lost + wrong symbols

Original: $P(x) = \dfrac{e^{-\lambda t}(\lambda t)^x}{x!}$

```
P (x)= e→ωt (ωt)x
x!
```

- Fraction split across two lines; superscripts flattened (`e^{-λt}` → `e→ωt`).
- Glyphs mapped to the **wrong Unicode characters**: `λ→ω`, `σ→ε`, `−→→`, `×→↑`, `√→→`.
  e.g. `dpois(8, 3 × 2)` became `dpois(8, 3 ↑ 2)`.
- This is the most dangerous kind: the output *looks* plausible, so errors are easy to miss.

### Failure case 2 — Sample2: brackets become digits

| Extracted | Intended |
|---|---|
| `R1x2=x-1 x2-4` | $R(x) = \dfrac{x-1}{x^2-4}$ |
| `1x+221x-22` | $(x+2)(x-2)$ |
| `5xƒxZ-2, xZ26` | $\{x \mid x \neq -2,\ x \neq 2\}$ |
| `/H110022` | $-2$ (unnamed glyph) |

- `( )→1 2`, `{ }→5 6`, `≠→Z`, `|→ƒ`, `≈→L`.
- Graph axis labels are mixed into the body text.
- pypdf warns that `fontTools` is needed to fully parse the CFF Type1 font encodings
  (one warning per font per page, ~100 lines for 12 pages). Not tested yet.

### Failure case 3 — Sample3: formulas absent

```
Power Rule:
Chain Rule:
```

Only headings are extracted; pages 3 and 5 are nearly empty.
Google Docs exports equations as vector drawings, so there is no text to extract.

### Why this happens

A PDF is a list of drawing instructions ("draw glyph #N at (x, y)"), not a structured document.

1. Math fonts often lack a correct glyph→Unicode map (`ToUnicode`), so glyphs decode as the wrong characters.
2. Fractions and exponents are only *positions* (smaller glyphs drawn higher/lower); the structure isn't stored.
3. Equations can be embedded as drawings/images, leaving no text at all.

**Conclusion:** plain text extraction is not reliable enough for math material.
Next step: test approach B (send the PDF directly to Claude, which reads page images as well as text).

## B. Direct PDF input to Claude (week 1, Fri)

Script: `scripts/claude_read_pdf.py` — sends the whole PDF as a base64 `document` block
and asks Claude (`claude-opus-5-5`) to transcribe it into Markdown with LaTeX math.
The API gives the model both the text layer **and** an image of every page.

### Results

| Sample | Pages | Input tokens | Input / page | Output tokens | Cost (USD) | Page separators |
|---|---|---|---|---|---|---|
| Sample1 | 5 | 11,638 | 2,328 | 3,199 | $0.11 | 5 / 5 |
| Sample2 | 12 | 31,763 | 2,647 | 15,849 | $0.44 | 12 / 12 |
| Sample3 | 6 | 10,889 | 1,815 | 2,817 | $0.10 | 6 / 6 |
| **Total** | 23 | | | | **$0.65** | |

None of the runs was cut off by `max_tokens` (32,000).

### The same failure cases, side by side

| Case | pypdf | Claude |
|---|---|---|
| Sample1 Poisson pmf | `e→ωt (ωt)x` / `x!` | $P(x) = e^{-\lambda t}\frac{(\lambda t)^x}{x!}$ |
| Sample1 std. dev. | `ε =` / `→` / `ωt` | $\sigma = \sqrt{\lambda t}$ |
| Sample1 R code | `dpois(8, 3 ↑ 2)` | `dpois(8, 3 * 2)` |
| Sample2 rational function | `R1x2=x-1 x2-4` | $R(x) = \frac{x-1}{x^2-4}$ |
| Sample2 domain | `5xƒxZ-2, xZ26` | $\{x \mid x \neq -2, x \neq 2\}$ |
| Sample2 graph | axis labels mixed into text | `[Figure: ... through $(1, 1)$ ...]` |
| Sample3 Power Rule | *(empty)* | $\frac{d}{dx}[x^n] = nx^{n-1}$ |
| Sample3 pages 3 & 5 | *(nearly empty)* | 20+ log / integral formulas |

### Observations

- Every symbol substitution seen with pypdf (`λ→ω`, `( )→1 2`, `≠→Z`, ...) is gone.
- Formulas embedded as drawings (Sample3) are read from the page image.
- Running headers/footers were removed and figures were summarized as instructed.
- Cost is dominated by **output** tokens ($20/MTok vs $4/MTok input):
  for Sample2, output was ~70% of the cost. The real app will send the PDF together
  with the question-generation prompt (no full transcription), so output will be much shorter.
- Rough input cost: ~2,000–2,700 tokens per page ≈ **$0.01 per page** on Opus 5.5.

### Open questions (to check on Sat)

- Did Claude **add or alter** anything not in the original? Needs line-by-line comparison
  against the PDF (e.g. Sample2 parenthetical limit notation).
- Are results consistent if the same PDF is sent twice?

## Comparison and decision (week 1, Sat)

_TODO_
