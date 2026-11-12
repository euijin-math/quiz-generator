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

_TODO_

## Comparison and decision (week 1, Sat)

_TODO_
