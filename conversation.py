"""In-memory conversation history sent again with every request."""

import os
import time


from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"
SYSTEM_INSTRUCTION = (
    "Eres un asistente breve. "
    "Respondes en español y en máximo dos frases."
)

history: list[dict] = []

MAX_TURNS = 10


def trim_history() -> None:
    """Keeps only the most recent complete conversation turns."""
    max_entries = MAX_TURNS * 2

    if len(history) > max_entries:
        del history[:-max_entries]

def send(message: str, retries: int = 0) -> str:
    """Sends one message and handles API errors with exponential backoff."""
    trim_history()

    history.append(
        {"role": "user", "parts": [{"text": message}]}
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=800,
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal",
                ),
            ),
        )

    except errors.ClientError as exc:
        history.pop()

        if exc.code == 429 and retries < 3:
            wait_seconds = 2 ** retries
            print(
                f"[429] Límite alcanzado. "
                f"Reintentando en {wait_seconds}s..."
            )
            time.sleep(wait_seconds)
            return send(message, retries=retries + 1)

        return (
            f"Error del cliente ({exc.code}): "
            f"{exc.message}. No se reintenta."
        )

    except errors.ServerError as exc:
        history.pop()

        if retries < 3:
            wait_seconds = 2 ** retries
            print(
                f"[{exc.code}] Error del servidor. "
                f"Reintentando en {wait_seconds}s..."
            )
            time.sleep(wait_seconds)
            return send(message, retries=retries + 1)

        return (
            f"El servicio no respondió tras varios intentos "
            f"({exc.code})."
        )

    finish_reason = str(response.candidates[0].finish_reason)

    if "MAX_TOKENS" in finish_reason:
        print("[warning] Respuesta truncada por max_output_tokens.")

    usage = response.usage_metadata
    print(
        f"[TOKENS] entrada={usage.prompt_token_count}, "
        f"respuesta={usage.candidates_token_count}, "
        f"total={usage.total_token_count}, "
        f"finish={finish_reason}"
    )

    response_text = response.text or ""

    history.append(
        {"role": "model", "parts": [{"text": response_text}]}
    )

    return response_text

def trigger_rate_limit() -> None:
    """Provokes a rate limit and confirms that the program keeps running."""
    global history

    history = []

    for request_number in range(1, 21):
        result = send(f"Cuenta hasta {request_number}.")
        print(f"Request {request_number}: {result}")

        if result.startswith("Error del cliente (429)"):
            print(
                "[OK] El error 429 fue manejado "
                "y el programa terminó sin caerse."
            )
            break

def demo_forgetting() -> None:
    """Demonstrates that a short sliding window forgets old information."""
    global history, MAX_TURNS

    original_max_turns = MAX_TURNS
    history = []
    MAX_TURNS = 3

    messages = [
        "Mi mascota se llama Rocko.",
        "Pregunta de relleno número 1.",
        "Pregunta de relleno número 2.",
        "Pregunta de relleno número 3.",
        "Pregunta de relleno número 4.",
        "Pregunta de relleno número 5.",
        "Pregunta de relleno número 6.",
        "¿Cómo se llama mi mascota?",
    ]

    try:
        for turn, message in enumerate(messages, start=1):
            print(f"\nDEMO — TURNO {turn}")
            print("USER:", message)
            print("BOT:", send(message))

            if turn < len(messages):
                print("[espera] 13 segundos...")
                time.sleep(13)
    finally:
        MAX_TURNS = original_max_turns
        history = []

def main() -> None:
    """Runs the required eight-turn conversation."""
    messages = [
        "Me llamo Alex y mi color favorito es el verde.",
        "¿Qué framework de Python vimos en la Clase 1?",
        "Dame un ejemplo de dato que no cabe en un int.",
        "¿Qué hace el comando uv init?",
        "Explica en una frase qué es un token.",
        "¿Qué significa que una API sea stateless?",
        "¿Para qué sirve un archivo .env?",
        "¿Cómo me llamo y cuál es mi color favorito?",
    ]

    for turn, message in enumerate(messages, start=1):
        print(f"\nTURNO {turn}")
        print("USER:", message)
        print("BOT:", send(message))

        if turn < len(messages):
            print("[espera] 13 segundos para respetar el límite de RPM...")
            time.sleep(13)


if __name__ == "__main__":
    main()
