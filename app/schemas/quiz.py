"""Pydantic models for a generated quiz (week 3, Mon).

Design: docs/schema-design.md  (read it first: the fields and rules come from there)

Claude returns JSON; these models turn it into Python objects and REJECT anything
that breaks our rules (raising pydantic.ValidationError).

Try it quickly:
    uv run python -c "from app.schemas.quiz import Quiz; print(Quiz.model_json_schema())"

Pydantic docs (v2) — read these sections:
    Models:      https://docs.pydantic.dev/latest/concepts/models/
    Fields:      https://docs.pydantic.dev/latest/concepts/fields/
                 (Field(min_length=..., max_length=...) works for str AND list)
    Validators:  https://docs.pydantic.dev/latest/concepts/validators/
                 (look for @model_validator(mode="after"))
    Literal types: `from typing import Literal`, e.g. Literal["a", "b"]
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

# Policy constants: the rest of the code (prompt, template, tests) should use
# these instead of writing 3 / 5 / "ABCDE" again.
MAX_PARTS = 3
NUM_CHOICES = 5
CHOICE_LETTERS = "ABCDE"


class Part(BaseModel):
    prompt: Annotated[str, Field(min_length=1)]
    choices: (
        Annotated[list[str], Field(min_length=NUM_CHOICES, max_length=NUM_CHOICES)]
        | None
    ) = None
    answer: Annotated[str, Field(min_length=1)]
    answer_value: str | None = None
    solution: Annotated[str, Field(min_length=1)]


class Question(BaseModel):
    type: Literal["multiple_choice", "short_answer", "free_response"]
    difficulty: Literal["easy", "medium", "hard"]
    topic: Annotated[str, Field(min_length=1)]
    stem: Annotated[str, Field(min_length=1)]
    figure: str | None = None
    parts: Annotated[list[Part], Field(min_length=1, max_length=MAX_PARTS)]

    @model_validator(mode="after")
    def check_type_rules(self):
        if self.type == "multiple_choice":
            for i, part in enumerate(self.parts, start=1):
                if part.choices is None:
                    raise ValueError(
                        f"Part {i}: There must be choices in a multiple choice problem."
                    )
                if part.answer not in list(CHOICE_LETTERS):
                    raise ValueError(
                        f"Part {i}: The answer key of a multiple choice problem must be one letter from {CHOICE_LETTERS}, got {part.answer!r}."
                    )
        else:
            for i, part in enumerate(self.parts, start=1):
                if part.choices is not None:
                    raise ValueError(
                        f"Part {i}: Answer choices are not allowed for a non multiple choice problem."
                    )
        if self.type == "short_answer":
            for i, part in enumerate(self.parts, start=1):
                if part.answer_value is None:
                    raise ValueError(
                        f"Part {i}: The short answer question must have the answer value."
                    )
        else:
            for i, part in enumerate(self.parts, start=1):
                if part.answer_value is not None:
                    raise ValueError(
                        f"Part {i}: There should not be answer value for non short answer problem."
                    )
        return self


class Quiz(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    questions: Annotated[list[Question], Field(min_length=1)]
