"""Calls Gemini and reports token usage and context budget."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"
CONTEXT_WINDOW_LIMIT = 1_048_576

SYSTEM_INSTRUCTION = (
    "Eres un instructor de programación para principiantes. "
    "Respondes en español, máximo 3 frases. "
    "Sin jerga sin explicar, sin inventar funciones."
)


def print_budget(contents: list[dict]) -> None:
    """Prints the input token count and context-window usage."""
    tokens = client.models.count_tokens(
        model=MODEL,
        contents=contents,
    )
    used_ratio = tokens.total_tokens / CONTEXT_WINDOW_LIMIT
    print(
        f"Historial: {tokens.total_tokens} tokens "
        f"({used_ratio:.4%} de la ventana)"
    )


def ask(prompt: str, temperature: float = 0.7) -> tuple[str, str]:
    """Returns the response text and finish reason."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": prompt}]},
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=temperature,
            max_output_tokens=800,
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal",
            ),
        ),
    )

    finish_reason = str(response.candidates[0].finish_reason)

    if "MAX_TOKENS" in finish_reason:
        print("[warning] La respuesta viene truncada por max_output_tokens.")

    usage = response.usage_metadata
    print(f"prompt    : {usage.prompt_token_count}")
    print(f"respuesta : {usage.candidates_token_count}")
    print(f"TOTAL     : {usage.total_token_count}")
    print(f"finish    : {finish_reason}")

    return response.text or "", finish_reason


def main() -> None:
    print("PRIMERA LLAMADA")
    first_text, _ = ask("Hola, me llamo Valeria.")
    print("BOT:", first_text)

    print("\nSEGUNDA LLAMADA")
    second_text, _ = ask("¿Cómo me llamo?")
    print("BOT:", second_text)


if __name__ == "__main__":
    main()
