"""Extract text from a PDF with pypdf (week 1, Thu).

Run with:  uv run python -m scripts.extract_text samples/Sample1.pdf
Output:    out/extract/<pdf name>.txt   (the out/ folder is git-ignored)

Purpose: see with your own eyes how math formulas break when a PDF is
turned into plain text. Tomorrow we compare this with sending the PDF
directly to Claude.
"""

import sys
from pathlib import Path

from pypdf import PdfReader

OUT_DIR = Path("out/extract")


if len(sys.argv) != 2:
    print("Usage: uv run python -m scripts.extract_text <path/to/file.pdf>")
    sys.exit(1)

filepath = sys.argv[1]

OUT_DIR.mkdir(parents=True, exist_ok=True)
new_filename = Path(filepath).stem
new_filename = new_filename + ".txt"
new_filepath = OUT_DIR / new_filename


reader = PdfReader(filepath)
total_pages = len(reader.pages)
total_characters = 0
with open(new_filepath, "w", encoding="utf-8") as f:
    for i, page in enumerate(reader.pages, start=1):
        f.write(f"==== Page {i} ====\n")
        text = page.extract_text()
        f.write(text)
        f.write("\n")
        total_characters += len(text)

print("===== Summary =====")
print("Total number of pages:", total_pages)
print("Total number of characters:", total_characters)


# ---------------------------------------------------------------------------
# TODO 4 (week 1, Thu): extract text from every page of a PDF
#
# Goal:
#   1. Read the PDF path from the command line.
#   2. Extract the text of every page.
#   3. Save it all to  out/extract/<pdf name without extension>.txt
#      with a separator line before each page, e.g.
#          ===== Page 1 =====
#   4. Print a short summary: number of pages and total characters.
#
# Hints:
#   - Command-line arguments are in  sys.argv  (a list of strings).
#     sys.argv[0] is the script itself, so the PDF path is sys.argv[1].
#     If no path was given, print a usage message and exit:  sys.exit(1)
#   - reader = PdfReader(path)
#     reader.pages            -> list-like of pages  (len() works)
#     page.extract_text()     -> str
#   - enumerate(reader.pages, start=1) gives you (page_number, page)
#   - Path("samples/Sample1.pdf").stem  -> "Sample1"
#   - Make sure the folder exists:  OUT_DIR.mkdir(parents=True, exist_ok=True)
#   - Write a file:  path.write_text(text, encoding="utf-8")
#
# Check:
#   Run it on all 3 samples, then open the .txt files next to the PDFs
#   and look for broken formulas (fractions, exponents, square roots,
#   integrals, Greek letters, matrices...).
# ---------------------------------------------------------------------------
