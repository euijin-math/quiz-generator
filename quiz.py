"""Command-line prototype: PDF + prompt -> quiz questions (week 2, Fri).

Run with:
    uv run python quiz.py samples/Sample1.pdf --n 5 --tier free
    uv run python quiz.py samples/Sample1.pdf --n 5 --tier free --prompt "Focus on R code"
    uv run python quiz.py --help

Output: out/quiz/<pdf name>.tex   (the out/ folder is git-ignored)

Order matters: we check the tier limits BEFORE calling the Claude API,
so a request that is over the limits never costs money.

Exit codes (a Unix convention: 0 = success, anything else = failure):
    0  success
    1  bad input (file missing, not a PDF, invalid numbers)
    2  usage error (argparse uses 2 automatically for wrong arguments)
    3  over the tier limits
    4  Claude API error
"""

import argparse
import logging
import sys
from io import BytesIO
from pathlib import Path

import anthropic
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.services.generator import generate_questions
from app.services.tiers import LimitExceededError, Tier, check_limits

OUT_DIR = Path("out/quiz")

EXIT_OK = 0
EXIT_BAD_INPUT = 1
EXIT_OVER_LIMIT = 3
EXIT_API_ERROR = 4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Read the command-line arguments.

    argv=None means "use sys.argv[1:]" (the real command line).
    Tests can pass a list instead, e.g. parse_args(["a.pdf", "--n", "3"]).
    """
    parser = argparse.ArgumentParser(
        description="Generate quiz questions (LaTeX) from a PDF with Claude."
    )

    parser.add_argument("pdf", type=Path, help="PDF file with the course material")
    parser.add_argument("--n", type=int, default=5, help="number of questions")
    parser.add_argument(
        "--tier",
        default="free",
        choices=[t.value for t in Tier],
        help="membership tier, which sets the limits (default: %(default)s)",
    )
    parser.add_argument("--prompt", default="", help="extra instructions for the quiz")

    return parser.parse_args(argv)


def count_pages(pdf_bytes: bytes) -> int:
    """Return the number of pages in a PDF given as bytes.

    Raises pypdf.errors.PdfReadError if the bytes are not a valid PDF.
    """
    return len(PdfReader(BytesIO(pdf_bytes)).pages)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an exit code (0 = success)."""
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    args = parse_args(argv)

    try:
        pdf_bytes = args.pdf.read_bytes()
        pages = count_pages(pdf_bytes)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except PdfReadError:
        print(f"Error: {args.pdf} is not a valid PDF file.", file=sys.stderr)
        return EXIT_BAD_INPUT

    try:
        check_limits(args.tier, pages, args.n, args.prompt)
    except LimitExceededError as e:
        print(f"Error: request is over the {e.tier} tier limits:", file=sys.stderr)
        for violation in e.violations:
            print(f"  - {violation}", file=sys.stderr)
        return EXIT_OVER_LIMIT
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_BAD_INPUT

    print(f"{args.pdf.name}: {pages} pages, {args.n} questions, tier={args.tier}")
    print("Generating... (this can take ~30 s)")

    try:
        result = generate_questions(pdf_bytes, args.n, args.prompt)
    except anthropic.APIError as e:
        print(f"Error: the Claude API request failed: {e}", file=sys.stderr)
        return EXIT_API_ERROR

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{args.pdf.stem}.tex"
    out_path.write_text(result.latex, encoding="utf-8")
    print(f"LaTeX file is saved to {out_path}")
    print(f"Tokens: {result.input_tokens} in / {result.output_tokens} out")
    if result.stop_reason == "max_tokens":
        print(
            "WARNING: the output was cut off (max_tokens). The .tex file is incomplete.",
            file=sys.stderr,
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
