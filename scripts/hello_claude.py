"""Minimal Claude API call (week 1, Wed).

Run with:  uv run python -m scripts.hello_claude
"""

import anthropic

from app.config import get_settings

settings = get_settings()

client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

response = client.messages.create(
    model=settings.claude_model,
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain Bezout's Rule in two sentences."}]
)


for block in response.content:
    if block.type == "text":
        print(block.text)

print("Input tokens:", response.usage.input_tokens)
print("Output tokens:", response.usage.output_tokens)
