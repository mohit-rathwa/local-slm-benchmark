# api/schemas.py
#
# Pydantic models define the exact shape of data going IN and OUT of our API.
# FastAPI uses these automatically to validate requests and responses.
# If a request is missing a field or has the wrong type, FastAPI rejects it
# with a clear error message — no extra code needed.

from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    """What the caller must send in the POST /generate request body."""

    model: str = Field(
        default="mistral",
        description="Which Ollama model to use",
        examples=["llama3", "mistral", "phi3:mini"],
    )
    prompt: str = Field(
        description="The question or instruction to send to the model",
        min_length=1,
        max_length=4000,
    )
    max_tokens: int = Field(
        default=512,
        ge=1,       # ge = greater than or equal to
        le=4096,    # le = less than or equal to
        description="Maximum number of tokens to generate",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creativity: 0=deterministic, 2=very random",
    )


class GenerateResponse(BaseModel):
    """What our API sends back after a successful generation."""

    model: str
    prompt: str
    response: str
    tokens_per_sec: float
    total_latency_ms: float
    time_to_first_token_ms: float


class ErrorResponse(BaseModel):
    """Returned when something goes wrong."""

    error: str
    detail: Optional[str] = None
