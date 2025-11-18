"""
Qwen3 Embedding Service for Agent Knowledge Base
-------------------------------------------------
Production-ready FastAPI service for generating high-dimensional embeddings
to support vector, relational, and graph databases in agent orchestration.

Features:
- OpenAI-compatible API for easy integration
- Async processing with batch size limits
- Proper error handling and validation
- Health checks and monitoring
- Environment-based configuration
- Structured logging
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import List, Union, Optional, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
import torch
import numpy as np

# ----- Logging Configuration -----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----- Configuration -----
class Config:
    """Centralized configuration using environment variables"""

    # Model settings
    MODEL_REPO: str = os.getenv("EMBEDDING_MODEL_REPO", "Qwen/Qwen3-Embedding-4B")
    MODEL_PATH: str = os.getenv(
        "EMBEDDING_MODEL_PATH",
        os.path.expanduser("~/.cache/embedding_models/Qwen3-Embedding-4B")
    )
    BASE_DIM: int = int(os.getenv("EMBEDDING_BASE_DIM", "2560"))

    # Performance settings
    MAX_BATCH_SIZE: int = int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", "32"))
    MAX_INPUT_LENGTH: int = int(os.getenv("EMBEDDING_MAX_INPUT_LENGTH", "8192"))
    REQUEST_TIMEOUT: float = float(os.getenv("EMBEDDING_REQUEST_TIMEOUT", "120.0"))

    # Server settings
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    ALLOW_ORIGINS: List[str] = os.getenv("EMBEDDING_ALLOW_ORIGINS", "*").split(",")

    # Dimension constraints
    MIN_DIM: int = 32

    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        if cls.BASE_DIM < cls.MIN_DIM:
            raise ValueError(f"BASE_DIM must be >= {cls.MIN_DIM}")
        if cls.MAX_BATCH_SIZE < 1:
            raise ValueError("MAX_BATCH_SIZE must be >= 1")
        logger.info(f"Configuration validated - Device: {cls.DEVICE}, Base Dim: {cls.BASE_DIM}")


# ----- Global State -----
class AppState:
    """Global application state"""
    model: Optional[SentenceTransformer] = None
    model_loaded: bool = False
    startup_time: Optional[float] = None
    request_count: int = 0
    total_embeddings_generated: int = 0


state = AppState()


# ----- Model Management -----
async def download_model_async() -> None:
    """Download model asynchronously if not present"""
    def _download():
        if not os.path.exists(Config.MODEL_PATH) or not os.listdir(Config.MODEL_PATH):
            logger.info(f"Downloading model {Config.MODEL_REPO} to {Config.MODEL_PATH}")
            os.makedirs(Config.MODEL_PATH, exist_ok=True)
            snapshot_download(
                repo_id=Config.MODEL_REPO,
                local_dir=Config.MODEL_PATH,
                local_dir_use_symlinks=False,
            )
            logger.info("Model download complete")
        else:
            logger.info(f"Model already exists at {Config.MODEL_PATH}")

    await asyncio.get_event_loop().run_in_executor(None, _download)


async def load_model() -> SentenceTransformer:
    """Load the embedding model with proper error handling"""
    try:
        logger.info("Loading embedding model...")

        def _load():
            return SentenceTransformer(
                Config.MODEL_PATH,
                device=Config.DEVICE,
            )

        model = await asyncio.get_event_loop().run_in_executor(None, _load)
        logger.info(f"Model loaded successfully on {Config.DEVICE}")
        return model

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Embedding Service...")
    Config.validate()

    try:
        await download_model_async()
        state.model = await load_model()
        state.model_loaded = True
        state.startup_time = time.time()
        logger.info("Embedding Service ready")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Embedding Service...")
    if Config.DEVICE == "cuda":
        torch.cuda.empty_cache()
    state.model = None
    state.model_loaded = False


# ----- FastAPI Application -----
app = FastAPI(
    title="Qwen3 Embedding Service",
    description="High-dimensional embedding service for agent knowledge bases",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Request/Response Schemas -----
class EmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request"""
    model: str
    input: Union[str, List[str]] = Field(..., description="Text(s) to embed")
    dimensions: Optional[int] = Field(
        None,
        description=f"Output dimension (32-{Config.BASE_DIM})",
        ge=Config.MIN_DIM,
        le=Config.BASE_DIM
    )
    encoding_format: Literal["float", "base64"] = Field(
        "float",
        description="Format for embeddings"
    )
    user: Optional[str] = Field(None, description="Optional user identifier")

    @field_validator('input')
    @classmethod
    def validate_input(cls, v):
        """Validate input is not empty"""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Input string cannot be empty")
            texts = [v]
        else:
            if not v:
                raise ValueError("Input list cannot be empty")
            if any(not t.strip() for t in v):
                raise ValueError("Input list contains empty strings")
            texts = v

        # Check batch size
        if len(texts) > Config.MAX_BATCH_SIZE:
            raise ValueError(
                f"Batch size {len(texts)} exceeds maximum {Config.MAX_BATCH_SIZE}"
            )

        # Check input length
        for i, text in enumerate(texts):
            if len(text) > Config.MAX_INPUT_LENGTH:
                raise ValueError(
                    f"Input {i} length {len(text)} exceeds maximum {Config.MAX_INPUT_LENGTH}"
                )

        return v


class EmbeddingData(BaseModel):
    """Single embedding result"""
    object: str = "embedding"
    index: int
    embedding: Union[List[float], str]  # str for base64


class Usage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    """OpenAI-compatible embedding response"""
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: Usage


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    device: str
    uptime_seconds: Optional[float] = None
    total_requests: int = 0
    total_embeddings: int = 0


class ErrorResponse(BaseModel):
    """Error response"""
    error: dict


# ----- Helper Functions -----
def _ensure_list(x: Union[str, List[str]]) -> List[str]:
    """Convert string input to list"""
    return [x] if isinstance(x, str) else x


def _estimate_tokens(texts: List[str]) -> int:
    """
    Estimate token count more accurately.
    For production, consider using actual tokenizer.
    """
    # Rough estimate: ~0.75 tokens per word for English
    total_chars = sum(len(t) for t in texts)
    total_words = sum(len(t.split()) for t in texts)
    # Use char-based estimate as backup
    return max(total_words, total_chars // 4)


async def _generate_embeddings(
    texts: List[str],
    dimensions: int,
    normalize: bool = True
) -> np.ndarray:
    """Generate embeddings asynchronously"""
    if not state.model_loaded or state.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service may be starting up."
        )

    def _encode():
        return state.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            batch_size=min(len(texts), Config.MAX_BATCH_SIZE),
        )

    try:
        # Run encoding in thread pool to avoid blocking
        embeddings = await asyncio.get_event_loop().run_in_executor(None, _encode)

        # Validate output dimensions
        if embeddings.shape[1] < dimensions:
            raise HTTPException(
                status_code=500,
                detail=f"Model produced {embeddings.shape[1]} dims, but {dimensions} requested"
            )

        # Truncate to requested dimensions
        if embeddings.shape[1] > dimensions:
            embeddings = embeddings[:, :dimensions]

        return embeddings

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


def _encode_base64(embedding: np.ndarray) -> str:
    """Encode embedding as base64 for efficient transmission"""
    import base64
    return base64.b64encode(embedding.astype(np.float32).tobytes()).decode('utf-8')


# ----- API Endpoints -----
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for orchestration platform"""
    uptime = None
    if state.startup_time:
        uptime = time.time() - state.startup_time

    return HealthResponse(
        status="healthy" if state.model_loaded else "starting",
        model_loaded=state.model_loaded,
        device=Config.DEVICE,
        uptime_seconds=uptime,
        total_requests=state.request_count,
        total_embeddings=state.total_embeddings_generated,
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check for kubernetes/orchestration"""
    if not state.model_loaded:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": Config.MODEL_REPO,
                "object": "model",
                "created": int(state.startup_time) if state.startup_time else 0,
                "owned_by": "organization",
                "permission": [],
                "root": Config.MODEL_REPO,
                "parent": None,
            }
        ]
    }


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    http_request: Request
):
    """
    Generate embeddings for text inputs.

    OpenAI-compatible endpoint for integration with various clients.
    Supports batch processing, dimension truncation, and multiple encoding formats.
    """
    start_time = time.time()

    # Update metrics
    state.request_count += 1

    try:
        # Parse input
        texts = _ensure_list(request.input)
        dimensions = request.dimensions or Config.BASE_DIM

        logger.info(
            f"Embedding request: {len(texts)} texts, "
            f"{dimensions} dims, user={request.user}"
        )

        # Generate embeddings with timeout
        try:
            embeddings = await asyncio.wait_for(
                _generate_embeddings(texts, dimensions),
                timeout=Config.REQUEST_TIMEOUT
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail=f"Request timed out after {Config.REQUEST_TIMEOUT}s"
            )

        # Update metrics
        state.total_embeddings_generated += len(texts)

        # Format response data
        data: List[EmbeddingData] = []
        for idx, vec in enumerate(embeddings):
            if request.encoding_format == "base64":
                embedding_data = _encode_base64(vec)
            else:
                embedding_data = [float(v) for v in vec]

            data.append(
                EmbeddingData(
                    index=idx,
                    embedding=embedding_data,
                )
            )

        # Estimate token usage
        token_count = _estimate_tokens(texts)

        elapsed = time.time() - start_time
        logger.info(f"Request completed in {elapsed:.2f}s")

        return EmbeddingResponse(
            data=data,
            model=request.model,
            usage=Usage(
                prompt_tokens=token_count,
                total_tokens=token_count,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": "Internal server error", "type": "server_error"}}
    )


# ----- Main Entry Point -----
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("EMBEDDING_PORT", "8000"))
    host = os.getenv("EMBEDDING_HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
