# api/main.py
#
# This is the FastAPI web server that wraps Ollama.
# It turns your local model into a proper REST API with docs.
#
# Run with:  uvicorn api.main:app --reload
# Then open: http://localhost:8000/docs  ← interactive API explorer (free!)

import time
from contextlib import asynccontextmanager

import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import GenerateRequest, GenerateResponse, ErrorResponse
from benchmark.metrics import now, calc_tokens_per_sec


# ── Startup check ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the server starts. Checks Ollama is reachable."""
    try:
        models = ollama.list()
        names = [m["name"] for m in models.get("models", [])]
        print(f"\n Ollama connected. Available models: {names}")
    except Exception:
        print("\n WARNING: Could not connect to Ollama. Is it running?")
        print("   Start it with: ollama serve")
    yield  # server runs here


# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Local SLM API",
    description=(
        "A FastAPI wrapper around Ollama that runs LLMs entirely offline.\n\n"
        "**Privacy**: No data leaves your machine.\n"
        "**Cost**: $0 per inference.\n"
        "**Latency**: No network round-trip."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow requests from any origin (useful for connecting a frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["health"])
def root():
    """Health check — returns OK if the server is running."""
    return {"status": "ok", "message": "Local SLM API is running"}


@app.get("/models", tags=["models"])
def list_models():
    """Returns all Ollama models currently available on this machine."""
    try:
        result = ollama.list()
        models = [m["name"] for m in result.get("models", [])]
        return {"models": models, "count": len(models)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama unavailable: {e}")


@app.post(
    "/generate",
    response_model=GenerateResponse,
    tags=["inference"],
    summary="Generate a response from a local model",
)
def generate(request: GenerateRequest):
    """
    Send a prompt to a local Ollama model and get back a response with metrics.

    - **model**: which model to use (must be pulled first)
    - **prompt**: your question or instruction
    - **max_tokens**: cap on response length
    - **temperature**: 0 = focused, 1 = balanced, 2 = creative
    """
    first_token_time = None
    full_response = ""
    start = now()

    try:
        stream = ollama.chat(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            stream=True,
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        )

        for chunk in stream:
            token = chunk["message"]["content"]
            if token:
                if first_token_time is None:
                    first_token_time = now()
                full_response += token

    except ollama.ResponseError as e:
        # Model not found or Ollama error
        raise HTTPException(
            status_code=404,
            detail=f"Model '{request.model}' not found. Pull it with: ollama pull {request.model}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    end = now()
    total_ms = round((end - start) * 1000, 1)
    ttft_ms = round((first_token_time - start) * 1000, 1) if first_token_time else 0
    token_count = len(full_response) // 4

    return GenerateResponse(
        model=request.model,
        prompt=request.prompt,
        response=full_response.strip(),
        tokens_per_sec=calc_tokens_per_sec(token_count, end - start),
        total_latency_ms=total_ms,
        time_to_first_token_ms=ttft_ms,
    )
