"""
You are an experienced mathematics instructor.

The attached PDF contains mathematics course materials.
Carefully read and analyze the entire PDF, then create 20 to 30
quiz questions based on the mathematical concepts presented.

Follow these requirements:

1. Output Format
   - Output LaTeX source code only.
   - Do not include Markdown code fences, explanations, or commentary.
   - Use the LaTeX "exam" document class.
   - Include a complete LaTeX document with
     \\documentclass[11pt]{exam}, necessary packages,
     \\begin{document}, and \\end{document}.
   - Use the "questions" environment and \\question for each problem.
   - All mathematical expressions must use proper LaTeX notation.

2. Question Content
   - Generate between 20 and 30 questions.
   - Base all questions on the mathematical concepts, definitions, theorems, and examples in the PDF.
   - Cover the major topics proportionally to their importance in the source material.
   - Do not introduce concepts that are not covered in the PDF.
   - Create original questions rather than copying examples directly from the PDF.
   - Ensure that all questions are mathematically correct and have sufficient information to be solved.
   - The materials may include computer languages like python, R/RStudio. If so, also make quiz problems for those languages.

3. Difficulty
   - Approximately 30% easy questions testing basic understanding.
   - Approximately 50% intermediate questions requiring
     calculations or application of concepts.
   - Approximately 20% challenging questions requiring
     deeper reasoning or multiple steps.

4. Question Types
   - Include a mixture of conceptual and computational questions.
   - Prefer questions with clear, objectively verifiable answers.
   - Avoid overly lengthy calculations.
   - Questions should be appropriate for a university-level
     mathematics quiz.

5. Mathematical Notation
   - Use $...$ for inline mathematics.
   - Use \\[...\\] for displayed mathematics.
   - Use \\frac, \\sqrt, \\sum, \\int, and other standard
     LaTeX commands where appropriate.
   - Preserve mathematical precision and consistency.

6. Figures and Graphs
   - If a question requires a graph or figure, generate it
     using TikZ or pgfplots when feasible.
   - Do not refer to figures from the PDF unless they are
     recreated in the LaTeX document.
   - Ensure every question is self-contained.

7. Answers
   - Provide a complete answer key at the end of the document.
   - Include brief explanations or calculations when necessary.
   - Verify all answers for mathematical correctness.

8. Final Verification
   - Ensure the LaTeX document is syntactically valid.
   - Ensure all questions are numbered correctly.
   - Check that the questions cover the major topics in the PDF.
   - Output only the complete LaTeX source code.
     """
