"""Unit tests for app/schemas/quiz.py (week 3, Mon).

Run with:  uv run pytest tests/test_schemas.py -v
"""

# TODO: write the tests for Part / Question / Quiz.
#
# Requirements:
#   1. One helper that returns a VALID question as a dict, with a way to change
#      only the fields a test cares about (so each test shows just what is different).
#      Each question type needs different part fields, so think about how the
#      helper builds valid parts for the given type.
#   2. Valid input is accepted: one test per question type (3 types).
#   3. Invalid input is rejected with pydantic.ValidationError. Cover at least:
#      - field rules: empty text, 0 parts, MAX_PARTS + 1 parts, wrong number of
#        choices, unknown type / difficulty, a quiz with 0 questions
#      - cross-field rules: every rule in Question's validator, including one case
#        where only the 2nd part is wrong (the message must say "Part 2")
#      - the multiple-choice answer: a wrong letter, lower case, and two letters ("AB")
#   4. Use @pytest.mark.parametrize + pytest.param(..., id="...") where several cases
#      share the same test body. Use the constants (MAX_PARTS, NUM_CHOICES,
#      CHOICE_LETTERS) instead of writing 3 / 5 / "ABCDE".
#   5. For validator rules, check the message too (pytest.raises(..., match=...)),
#      so the test fails if the wrong rule rejected the input.
#
# Reminder: you already used pytest.raises / parametrize / pytest.param in
# tests/test_tiers.py and tests/test_generator.py.
