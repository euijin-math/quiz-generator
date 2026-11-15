"""Unit tests for app/services/tiers.py (week 2).

Run with:  uv run pytest tests/test_tiers.py -v
"""

import pytest

from app.services.tiers import (
    TIER_LIMITS,
    LimitExceededError,
    Tier,
    check_limits,
    count_prompt_lines,
    get_limits,
)


def make_prompt(n_lines: int) -> str:
    """Build a prompt with exactly n non-blank lines, e.g. 'line 1\\nline 2'."""
    return "\n".join(f"line {i}" for i in range(1, n_lines + 1))


# ---------------------------------------------------------------------------
# get_limits  (example tests, already written: read them first)
# ---------------------------------------------------------------------------


def test_get_limits_free():
    limits = get_limits("free")
    assert limits.max_pages == 10
    assert limits.max_questions == 5
    assert limits.max_prompt_lines == 3


def test_get_limits_unknown_tier_raises():
    # pytest.raises PASSES only if the code inside the `with` block raises
    # that exception. If nothing is raised, the test FAILS.
    with pytest.raises(ValueError):
        get_limits("gold")


# @pytest.mark.parametrize runs the SAME test once per case in the list.
# Each pytest.param(...) supplies the arguments (prompt, expected) in order;
# its id is the name shown with -v, e.g. test_count_prompt_lines[windows-crlf].


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        pytest.param("", 0, id="empty"),
        pytest.param("Focus on limits", 1, id="single-line"),
        pytest.param(
            """This is a test docstring.
         consisting of multiple lines.
          
           also, some blank. lines.
                  
                   Hello~ """,
            4,
            id="indented-lines-and-whitespace-only-lines",
        ),
        pytest.param(
            """

This is the second set of the doc string.

for the test

         
          
Bye! """,
            3,
            id="leading-blank-lines",
        ),
        pytest.param(
            """This is another
         
          set of doctring.
           
            
                  
                          
                            
                             
                              
                                 With some blank lines too.
                                  
                                   Bye """,
            4,
            id="many-consecutive-whitespace-only-lines",
        ),
        pytest.param(
            "This is the \nLast test line\n\n    \n \n that's it.\n\r\n",
            3,
            id="mixed-lf-and-crlf",
        ),
        pytest.param("line A\nline B\n", 2, id="trailing-newline"),
        pytest.param("line A\n\n   \nline B", 2, id="blank-and-whitespace-lines"),
        pytest.param("line A\r\nline B\r\n", 2, id="windows-crlf"),
    ],
)
def test_count_prompt_lines(prompt, expected):
    assert count_prompt_lines(prompt) == expected


# ---------------------------------------------------------------------------
# check_limits: 3 tiers x 3 limits  (the core of this file)
#
# For every tier, test the BOUNDARY:
#   - exactly at the limit   -> allowed (no exception)
#   - limit + 1              -> LimitExceededError
#
# Boundaries are where bugs live: `<` vs `<=` is the classic off-by-one error.
# Read limits from TIER_LIMITS instead of hard-coding 10 / 30 / 100,
# so the tests keep working if we change the numbers later.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tier", list(Tier))
def test_at_limits_is_allowed(tier):
    limits = TIER_LIMITS[tier]
    # Should NOT raise. If it raises, pytest reports the test as failed.
    check_limits(
        tier,
        pages=limits.max_pages,
        questions=limits.max_questions,
        prompt=make_prompt(limits.max_prompt_lines),
    )


@pytest.mark.parametrize("tier", list(Tier))
def test_too_many_pages_is_rejected(tier):
    limits = TIER_LIMITS[tier]
    with pytest.raises(LimitExceededError) as exc_info:
        check_limits(
            tier,
            pages=limits.max_pages + 1,
            questions=1,
            prompt="",
        )
    # exc_info.value is the exception object that was raised.
    assert len(exc_info.value.violations) == 1
    assert "pages" in exc_info.value.violations[0]


@pytest.mark.parametrize("tier", list(Tier))
def test_too_many_questions_is_rejected(tier):
    limits = TIER_LIMITS[tier]
    with pytest.raises(LimitExceededError) as exc_info:
        check_limits(
            tier, pages=limits.max_pages, questions=limits.max_questions + 1, prompt=""
        )

    assert len(exc_info.value.violations) == 1
    assert "questions" in exc_info.value.violations[0]


@pytest.mark.parametrize("tier", list(Tier))
def test_too_many_prompt_lines_is_rejected(tier):
    limits = TIER_LIMITS[tier]
    prompt = make_prompt(limits.max_prompt_lines + 1)
    with pytest.raises(LimitExceededError) as exc_info:
        check_limits(
            tier, pages=limits.max_pages, questions=limits.max_questions, prompt=prompt
        )
    assert len(exc_info.value.violations) == 1
    assert "Prompt" in exc_info.value.violations[0]


def test_all_violations_reported_together():
    tier = Tier.FREE
    limits = TIER_LIMITS[tier]
    prompt = make_prompt(limits.max_prompt_lines + 1)
    with pytest.raises(LimitExceededError) as exc_info:
        check_limits(
            tier,
            pages=limits.max_pages + 1,
            questions=limits.max_questions + 1,
            prompt=prompt,
        )
    assert len(exc_info.value.violations) == 3
    assert "pages" in exc_info.value.violations[0]
    assert "questions" in exc_info.value.violations[1]
    assert "Prompt" in exc_info.value.violations[2]


@pytest.mark.parametrize("tier", list(Tier))
def test_invalid_input_raises_value_error(tier):
    limits = TIER_LIMITS[tier]
    with pytest.raises(ValueError, match="pages"):
        check_limits(tier, pages=0, questions=limits.max_questions, prompt="a")
    with pytest.raises(ValueError, match="questions"):
        check_limits(tier, pages=1, questions=0, prompt="a")
