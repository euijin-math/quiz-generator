"""Send a PDF directly to Claude and get a Markdown + LaTeX transcription (week 1, Fri).

Run with:  uv run python -m scripts.claude_read_pdf samples/Sample1.pdf
Output:    out/claude/<pdf name>.md   (the out/ folder is git-ignored)

Compare the result with out/extract/<pdf name>.txt from yesterday.

API limits for PDF input (check the official docs: "PDF support"):
  - max request size 32 MB, max 600 pages per request
  - each page is sent as BOTH extracted text AND a page image,
    so a page costs roughly 1,500-3,000 input tokens.
"""

import base64
import sys
from pathlib import Path

import anthropic

from app.config import get_settings

OUT_DIR = Path("out/claude")

# Prices in USD per 1M tokens (Claude Opus 5.5). Used only for a rough cost estimate.
INPUT_PRICE_PER_MTOK = 4.00
OUTPUT_PRICE_PER_MTOK = 20.00


if len(sys.argv) != 2:
    print("Usage: uv run python -m scripts.claude_read_pdf <filepath/filename.pdf>")
    sys.exit(1)

pdf_path = Path(sys.argv[1])

PROMPT = """
You are given a PDF document containing mathematical educational materials. Your task is to accurately transcribe the entire document into Markdown, following the instructions below.

### 1. Output Format
- Output the transcription in **Markdown format only**.
- Do not include any introductory remarks, explanations, summaries, or commentary before or after the transcription.
- Preserve the original wording, mathematical notation, and logical structure as closely as possible.
- Use Markdown headings, paragraphs, lists, and tables to reflect the structure of the original document.
- Do not paraphrase, simplify, correct, or omit any mathematical content.

### 2. Mathematical Expressions
- Transcribe **all mathematical expressions using LaTeX notation**.
- Use `$...$` for inline mathematical expressions.
- Use `$$...$$` for displayed equations or expressions that appear on separate lines.
- Properly represent fractions, exponents, subscripts, Greek letters, integrals, summations, matrices, and other mathematical symbols using standard LaTeX commands.
- Preserve the original mathematical meaning and notation exactly.

### 3. Page Separation
- Clearly indicate the beginning of each PDF page using the following separator:

  `==== Page 1 ====`

- Replace `1` with the corresponding PDF page number.
- Place this separator at the very beginning of each page's transcription.
- Maintain the original page order and do not merge content across page boundaries.
- Include a separator for every page, even if the page contains no transcribable body text.

### 4. Headers, Footers, and Page Numbers
- Ignore all recurring page headers, footers, and printed page numbers.
- Do not transcribe decorative elements or other nonessential page formatting.
- Preserve section titles, subsection headings, definitions, theorems, examples, and exercises that are part of the main content.

### 5. Figures, Graphs, and Diagrams
- Do not attempt to reproduce figures, graphs, or diagrams visually.
- Instead, replace each figure with a **concise, one-line description** enclosed in square brackets, beginning with `[Figure: ...]`.
- Describe the mathematically relevant features of the figure, including its shape, labeled points, curves, intersections, extrema, inflection points, asymptotes, and other important properties when visible.
- Use LaTeX math notation for all mathematical expressions within figure descriptions.
- Do not separately transcribe every axis label or graphical annotation. Incorporate relevant information into the description.
- Do not infer mathematical properties that cannot be reliably determined from the figure.

**Example:**

`[Figure: A graph of a cubic polynomial with two turning points at $(x_1,y_1)$ and $(x_2,y_2)$, increasing for $x < x_1$ and $x > x_2$, and decreasing for $x_1 < x < x_2$.]`

### 6. Accuracy and Completeness
- Transcribe all main body text, mathematical expressions, definitions, theorems, proofs, examples, and exercises.
- Preserve the original order and organization of the material.
- Do not add explanations, interpretations, or mathematical information that is not explicitly present in the PDF.
- If any text or mathematical expression is unreadable, mark it as `[Illegible]` rather than guessing.
- Ensure that no substantive mathematical content is omitted.

### 7. Final Output Requirements
- Return only the complete Markdown transcription.
- Begin the output with `==== Page 1 ====`.
- Use consistent LaTeX formatting throughout the document.
- Do not wrap the entire output in a Markdown code block.
- Do not include any additional commentary.
"""


settings = get_settings()

client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")


with client.messages.stream(
    model=settings.claude_model,
    max_tokens=32000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": PROMPT},
            ],
        }
    ],
) as stream:
    response = stream.get_final_message()

OUT_DIR.mkdir(parents=True, exist_ok=True)
new_filename = pdf_path.stem
new_filename = new_filename + ".md"
new_filepath = OUT_DIR / new_filename

with open(new_filepath, "w", encoding="utf-8") as f:
    for block in response.content:
        if block.type == "text":
            f.write(block.text)

input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
cost = (
    input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
    + output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK
)

print("Input tokens:", input_tokens)
print("Output tokens:", output_tokens)
print("Cost:", f"${cost:.4f}")

if response.stop_reason == "max_tokens":
    print("⚠️ WARNING: output was cut off. Increase max_tokens.")
print("Stop reason:", response.stop_reason)
