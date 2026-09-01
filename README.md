# Curso MCP — hjnarvaez

Repositorio de prácticas del curso, desarrollado con Python 3.12 y `uv`.

## Clase 1 — Preparación del entorno

Se verificó la instalación y funcionamiento de las herramientas necesarias:

| Componente | Estado | Versión o detalle |
|---|---:|---|
| Python 3.12 | OK | 3.12.14 |
| uv | OK | 0.12.6 |
| Git | OK | 2.50.1 |
| Docker | OK | 29.7.2 |
| Protección de `.env` | OK | Incluido en `.gitignore` |

## Clase 2 — APIs de IA Generativa y memoria conversacional

### Objetivo

Construir un cliente para Gemini que permita:

- configurar el comportamiento del modelo mediante una instrucción de sistema;
- controlar temperatura, límite de salida y nivel de razonamiento;
- registrar el consumo de tokens y la causa de finalización;
- mantener memoria conversacional reenviando el historial;
- limitar el historial mediante una ventana deslizante;
- manejar errores de cuota `429` con reintentos exponenciales.

### Requisitos

- Python 3.12 o superior.
- `uv`.
- Una clave válida de Gemini API.

Las dependencias utilizadas están declaradas en `pyproject.toml`:

- `google-genai`;
- `python-dotenv`;
- `rich`.

### Instalación

Clonar el repositorio e instalar las dependencias:

```bash
git clone https://github.com/hjnarvaez/curso-mcp-hjnarvaez.git
cd curso-mcp-hjnarvaez
uv sync
```

### Configuración segura

Crear el archivo local de variables de entorno:

```bash
cp .env.example .env
```

Completar la clave dentro de `.env`:

```dotenv
GEMINI_API_KEY=coloca_aqui_tu_clave
```

El archivo `.env` está excluido mediante `.gitignore` y no debe subirse al repositorio.

### Ejecución

Cliente básico, configuración del modelo y medición de tokens:

```bash
uv run python gemini_client.py
```

Conversación de ocho turnos con memoria:

```bash
uv run python conversation.py
```

Prueba controlada del manejo del límite de cuota:

```bash
uv run python -c "import conversation; conversation.trigger_rate_limit()"
```

> La prueba del límite consume solicitudes de la cuota de Gemini. No es necesario repetirla si ya existe la evidencia.

### Implementación

#### `gemini_client.py`

Realiza llamadas independientes al modelo `gemini-3.6-flash`, aplica una instrucción de sistema y muestra:

- tokens del prompt;
- tokens de la respuesta;
- tokens totales;
- motivo de finalización;
- advertencia cuando la respuesta alcanza `MAX_TOKENS`.

#### `conversation.py`

Conserva el historial en memoria y lo envía nuevamente en cada solicitud. La conversación usa una ventana deslizante de hasta 10 turnos completos para evitar un crecimiento indefinido del contexto.

También captura errores del cliente y del servidor. Para un error `429`, ejecuta hasta tres reintentos con espera exponencial de 1, 2 y 4 segundos. Si la cuota continúa agotada, devuelve un mensaje controlado y el programa termina sin caerse.

### Resultados y evidencias

| Evidencia | Resultado comprobado |
|---|---|
| [Conversación con memoria](entregas/s02/evidencia/memoria.txt) | Ocho turnos completos. En el turno 8 recuerda que el usuario se llama Alex y que su color favorito es el verde. |
| [Manejo del error 429](entregas/s02/evidencia/rate_limit.txt) | Registra los reintentos de 1, 2 y 4 segundos y confirma que el programa finaliza sin `Traceback`. |

En la conversación se observa que los tokens de entrada aumentan conforme crece el historial. El último turno terminó con `FinishReason.STOP` y un total de 419 tokens.

La advertencia del SDK sobre el uso directo de AFC es informativa y no impide la ejecución ni invalida las evidencias.

### Conversación de 8 turnos (Paso 7)

Ver evidencia en [`entregas/s02/evidencia/memoria.txt`](entregas/s02/evidencia/memoria.txt).

La salida completa obtenida fue:

Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.

TURNO 1
USER: Me llamo Alex y mi color favorito es el verde.
[TOKENS] entrada=30, respuesta=20, total=50, finish=FinishReason.STOP
BOT: ¡Mucho gusto, Alex! El verde es un color excelente, lleno de vida y naturaleza.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 2
USER: ¿Qué framework de Python vimos en la Clase 1?
[TOKENS] entrada=64, respuesta=30, total=94, finish=FinishReason.STOP
BOT: No me has mencionado qué vieron en tu Clase 1. Si me das más contexto o las opciones, con gusto te ayudo a recordarlo.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 3
USER: Dame un ejemplo de dato que no cabe en un int.
[TOKENS] entrada=108, respuesta=73, total=181, finish=FinishReason.STOP
BOT: En Python los enteros no tienen límite, pero en lenguajes como C o Java, el número `3,000,000,000` no cabe en un `int` estándar de 32 bits. También un número con decimales, como `3.14`, requiere un tipo de dato flotante (`float`).
[espera] 13 segundos para respetar el límite de RPM...

TURNO 4
USER: ¿Qué hace el comando uv init?
[TOKENS] entrada=191, respuesta=43, total=234, finish=FinishReason.STOP
BOT: El comando `uv init` crea un nuevo proyecto de Python inicializando un archivo de configuración `pyproject.toml` en el directorio actual. También puede generar la estructura básica de archivos si el directorio está vacío.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 5
USER: Explica en una frase qué es un token.
[TOKENS] entrada=246, respuesta=36, total=282, finish=FinishReason.STOP
BOT: Un token es la unidad básica de texto —como una palabra, una subpalabra o un carácter— que los modelos de inteligencia artificial utilizan para procesar y comprender el lenguaje.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 6
USER: ¿Qué significa que una API sea stateless?
[TOKENS] entrada=293, respuesta=39, total=332, finish=FinishReason.STOP
BOT: Significa que el servidor no guarda ninguna información ni contexto sobre las peticiones anteriores del cliente. Por lo tanto, cada solicitud debe contener toda la información necesaria para ser procesada de forma independiente.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 7
USER: ¿Para qué sirve un archivo .env?
[TOKENS] entrada=343, respuesta=51, total=394, finish=FinishReason.STOP
BOT: Un archivo `.env` sirve para almacenar variables de entorno y datos sensibles, como claves de API o contraseñas, de forma segura y separada del código fuente. Esto permite configurar el entorno de la aplicación sin exponer información confidencial en el repositorio.
[espera] 13 segundos para respetar el límite de RPM...

TURNO 8
USER: ¿Cómo me llamo y cuál es mi color favorito?
[TOKENS] entrada=408, respuesta=11, total=419, finish=FinishReason.STOP
BOT: Te llamas Alex y tu color favorito es el verde.
```text

```

### Por qué elegí ventana deslizante

Elegí la ventana deslizante porque esta práctica utiliza una conversación corta y solo necesita conservar los últimos turnos. Esta estrategia es sencilla, consume menos contexto y evita que el historial crezca indefinidamente. No utilicé resumen progresivo, memoria selectiva ni almacenamiento externo porque en este ejercicio no necesitamos recordar información entre diferentes sesiones.

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en [`entregas/s02/evidencia/rate_limit.txt`](entregas/s02/evidencia/rate_limit.txt).

El error `429` fue capturado y manejado mediante reintentos exponenciales de 1, 2 y 4 segundos. Después de agotar los reintentos, el programa mostró un mensaje controlado y terminó sin producir un `Traceback`.

### Configuración utilizada

La práctica se ejecutó con `gemini-3.6-flash` y `thinking_level="minimal"`. Se mantuvieron explícitos `system_instruction`, `temperature` y `max_output_tokens`.


### Estructura principal

```text
.
├── .env.example
├── conversation.py
├── gemini_client.py
├── pyproject.toml
├── uv.lock
└── entregas/
    └── s02/
        └── evidencia/
            ├── memoria.txt
            └── rate_limit.txt
```
