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

## Semana 2 — Gemini API, memoria y manejo de errores

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
