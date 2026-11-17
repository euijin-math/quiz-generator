"""Try prompt v1: generate N questions from a PDF (week 2, Mon).

Run with:  uv run python -m scripts.try_generate samples/Sample1.pdf 5
           uv run python -m scripts.try_generate samples/Sample1.pdf 5 "Focus on R code"
Output:    out/generate/<pdf name>.tex   (the out/ folder is git-ignored)

This is a throwaway test script. The real command-line tool (quiz.py, with
--tier and --prompt) comes later this week.
"""

import sys
import time
from pathlib import Path

from app.services.generator import generate_questions

# Prices in USD per 1M tokens (Claude Opus 5.5). Rough estimate only.
INPUT_PRICE_PER_MTOK = 4.00
OUTPUT_PRICE_PER_MTOK = 20.00

OUT_DIR = Path("out/generate")

if len(sys.argv) not in (3, 4):
    print(
        'Usage: uv run python -m scripts.try_generate <path/to/file.pdf> <n> ["prompt"]'
    )
    sys.exit(1)

pdf_path = Path(sys.argv[1])
n = int(sys.argv[2])
user_prompt = sys.argv[3] if len(sys.argv) == 4 else ""

start = time.perf_counter()
result = generate_questions(pdf_path.read_bytes(), n, user_prompt)
elapsed = time.perf_counter() - start

OUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUT_DIR / f"{pdf_path.stem}.tex"
out_path.write_text(result.latex, encoding="utf-8")

cost = (
    result.input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
    + result.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK
)
print(f"Saved:         {out_path}")
print(f"Time:          {elapsed:.1f} s")
print(f"Input tokens:  {result.input_tokens}")
print(f"Output tokens: {result.output_tokens}")
print(f"Cost:          ${cost:.4f}")
print(f"Stop reason:   {result.stop_reason}")
if result.stop_reason == "max_tokens":
    print("WARNING: output was cut off. Increase MAX_TOKENS.")
