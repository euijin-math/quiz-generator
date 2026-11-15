"""Per-tier usage limits (week 2).

Every request is checked against the user's tier BEFORE calling the Claude API,
so a free user can never trigger an expensive call.

Week 2: used by the CLI (`quiz.py --tier free`).
Week 5: the same functions are called with the tier stored on the user in the DB.
"""

from dataclasses import dataclass
from enum import StrEnum


class Tier(StrEnum):
    """Membership tiers. A StrEnum member behaves like its string value:
    Tier.FREE == "free" is True, and Tier("free") returns Tier.FREE."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


@dataclass(frozen=True)
class TierLimits:
    """Upper limits for one request. frozen=True makes instances read-only."""

    max_pages: int
    max_questions: int
    max_prompt_lines: int


# Values from the project plan. Adjust later after looking at real API costs.
TIER_LIMITS: dict[Tier, TierLimits] = {
    Tier.FREE: TierLimits(max_pages=10, max_questions=5, max_prompt_lines=3),
    Tier.BASIC: TierLimits(max_pages=30, max_questions=20, max_prompt_lines=10),
    Tier.PRO: TierLimits(max_pages=100, max_questions=50, max_prompt_lines=30),
}


class LimitExceededError(Exception):
    """Raised when a request goes over one or more limits of the user's tier.

    `violations` holds one human-readable reason per exceeded limit, e.g.
    ["PDF has 12 pages, but the free tier allows at most 10."]
    """

    def __init__(self, tier: Tier, violations: list[str]) -> None:
        self.tier = tier
        self.violations = violations
        super().__init__("; ".join(violations))


def get_limits(tier: str) -> TierLimits:
    """Return the limits for a tier name such as "free".

    Raises ValueError for an unknown tier name.
    """

    return TIER_LIMITS[Tier(tier)]


def count_prompt_lines(prompt: str) -> int:
    """Count the lines of a user prompt, ignoring blank lines.

    Examples:
        ""                      -> 0
        "Focus on limits"       -> 1
        "line A\\nline B\\n"      -> 2   (trailing newline is not an extra line)
        "line A\\n\\n   \\nline B" -> 2   (blank / whitespace-only lines don't count)
    """

    return sum(1 for line in prompt.splitlines() if line.strip())


def check_limits(tier: str, pages: int, questions: int, prompt: str) -> None:
    """Check one request against the tier's limits.

    Returns None if everything is within limits.
    Raises:
        ValueError: unknown tier, or pages / questions smaller than 1.
        LimitExceededError: one or more limits exceeded. ALL exceeded limits
            are reported together, not just the first one.
    """

    limits = get_limits(tier)
    violations: list[str] = []

    if pages < 1:
        raise ValueError(
            f"Number of pages must be at least 1, but received {pages} page."
        )

    if questions < 1:
        raise ValueError(
            f"Number of questions must be at least 1, but received {questions} questions."
        )

    if limits.max_pages < pages:
        violations.append(
            f"PDF has {pages} pages, but the {tier} tier allows at most {limits.max_pages}."
        )

    if limits.max_questions < questions:
        violations.append(
            f"Requested {questions} questions, but the {tier} tier allows at most {limits.max_questions}."
        )

    prompt_lines = count_prompt_lines(prompt)
    if prompt_lines > limits.max_prompt_lines:
        violations.append(
            f"Prompt has {prompt_lines} lines, but the {tier} tier allows at most {limits.max_prompt_lines}."
        )

    if violations:
        raise LimitExceededError(Tier(tier), violations)
