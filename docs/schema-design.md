# Question Schema Design (week 3)

From week 3, Claude returns quiz questions as **structured JSON** instead of a full
LaTeX document. Our code validates the JSON (Pydantic) and renders it with our own
LaTeX template. Claude writes the content; our code owns the format and the rules.

Why:

- Rules such as "exactly N questions" and "at most 3 parts" can be **checked in code**,
  not only asked for in the prompt.
- Answers can be **verified automatically** (SymPy, week 4).
- The same data can produce different outputs (quiz with or without answer key)
  and can be stored per question in the database (week 5).

## Structure

```
Quiz
 ├─ title: str
 └─ questions: list[Question]              exactly N

Question
 ├─ type: "multiple_choice" | "short_answer" | "free_response"
 ├─ difficulty: "easy" | "medium" | "hard"
 ├─ topic: str                              which topic/section of the PDF
 ├─ stem: str                               shared question text (LaTeX fragment)
 ├─ figure: str | None                      TikZ/pgfplots code, only when needed
 └─ parts: list[Part]                       1 to 3

Part
 ├─ prompt: str                             the task (LaTeX fragment)
 ├─ choices: list[str] | None               multiple_choice only: exactly 5 (A–E)
 ├─ answer: str                             final answer, human-readable (LaTeX)
 ├─ answer_value: str | None                short_answer only: SymPy-readable value
 └─ solution: str                           model solution (LaTeX)
```

All text fields are **LaTeX fragments**: plain text with `$...$` / `\[...\]` math,
no `\documentclass`, no environments that belong to the template.

## Decisions

| # | Decision | Reason |
|---|---|---|
| 1 | `type` is per **question**, not per part | Mixed-type questions are rare; simpler data and templates. |
| 2 | Every question has **1–3 parts**; a question without sub-parts has exactly 1 part | One code path instead of "has parts / has no parts" branches. The template omits the "(a)" label when there is only 1 part. |
| 3 | Multiple choice: exactly **5 choices**; `answer` is a letter `"A"`–`"E"` | Fixed format, easy to check and to shuffle later. |
| 4 | Short answer: `answer_value` is a SymPy-readable expression (e.g. `"3/8"`, `"0.2381"`, `"sqrt(2)/2"`) | Needed for automatic checking in week 4. |
| 5 | Numeric tolerance **1e-4** by default, set in **our code**, not in the JSON | The model should not choose how strictly its own answer is checked. |
| 6 | Free response: a **model solution** only, no rubric | Grading open answers stays with a human instructor; enough for this project's scope. |
| 7 | No points, source pages, or time estimates for now | Not needed yet; easy to add later as optional fields. |

## Validation rules (checked in code)

Some rules fit in a JSON schema; the cross-field ones are checked by Pydantic
after the response arrives. Any violation → the response is rejected (week 3 Thu:
retry with the error message).

- `len(questions) == N` (N from the request, so checked outside the model class)
- `1 <= len(parts) <= 3`
- `type == "multiple_choice"` ⇒ every part has exactly 5 `choices` and
  `answer` in `A`–`E`
- `type != "multiple_choice"` ⇒ `choices` is `None`
- `type == "short_answer"` ⇒ every part has an `answer_value`
- `type != "short_answer"` ⇒ `answer_value` is `None`
- Text fields are not empty

## Open questions

- Should `answer_value` be required for every short-answer part? Current decision:
  **yes**, so short-answer questions are always machine-checkable; non-numeric
  answers (e.g. "Poisson") go into multiple choice or free response instead.
  Revisit if this makes the questions too narrow.
- Tolerance: absolute `|a - b| <= 1e-4` for now. Large values may need a relative
  tolerance (decide in week 4).
- Cross-field rules (e.g. "multiple choice ⇒ choices required") live in a
  `model_validator`, so they do **not** appear in the JSON schema Claude sees; they
  must also be stated in the prompt. Alternative: one model per question type
  (discriminated union on `type`), which puts these rules into the schema itself.
  Revisit if Claude often breaks them (and check how well structured outputs
  support `anyOf`).
- Template: the plan says `article` + `amsmath`; week 2 used the `exam` class.
  Decide on Tue when writing the template.
