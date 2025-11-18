# Qwen3 Embedding Service

Production-ready FastAPI service for generating high-dimensional embeddings to support vector, relational, and graph databases in agent orchestration platforms.

## Key Improvements Over Original Code

### 1. **Production Configuration**
- ✅ Environment-based configuration (no hard-coded paths)
- ✅ Cross-platform compatibility (Windows, Linux, macOS)
- ✅ Configurable via `.env` file
- ✅ Validation on startup

### 2. **Async/Performance**
- ✅ Fully async API using `asyncio`
- ✅ Batch size limiting to prevent OOM errors
- ✅ Request timeout handling
- ✅ Thread pool execution for CPU-bound operations
- ✅ CUDA memory management on shutdown

### 3. **Robustness & Error Handling**
- ✅ Comprehensive input validation
- ✅ Empty string detection
- ✅ Maximum length checks
- ✅ Proper error responses with HTTP status codes
- ✅ Global exception handler
- ✅ Graceful degradation

### 4. **Monitoring & Observability**
- ✅ Structured logging with timestamps
- ✅ Health check endpoint (`/health`)
- ✅ Readiness endpoint (`/ready`) for K8s
- ✅ Request metrics (count, embeddings generated)
- ✅ Performance timing logs

### 5. **API Enhancements**
- ✅ OpenAI-compatible `/v1/embeddings` endpoint
- ✅ `/v1/models` endpoint for model listing
- ✅ Base64 encoding support for efficient transmission
- ✅ Better token estimation
- ✅ User tracking field
- ✅ CORS support for web clients

### 6. **Application Lifecycle**
- ✅ Proper startup/shutdown with `lifespan` context manager
- ✅ Model loading in startup event (not at import time)
- ✅ Resource cleanup on shutdown
- ✅ Service readiness tracking

### 7. **Security & Validation**
- ✅ Input length limits (prevent DoS)
- ✅ Batch size limits (prevent resource exhaustion)
- ✅ CORS configuration
- ✅ Request validation with Pydantic v2
- ✅ Type safety throughout

### 8. **Developer Experience**
- ✅ Comprehensive documentation
- ✅ Client example code
- ✅ Usage examples for common patterns
- ✅ Clear error messages
- ✅ Integration examples with vector/graph DBs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_embedding.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Service

```bash
python embedding_service.py
```

Or with uvicorn for production:

```bash
uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Test the Service

```bash
# Check health
curl http://localhost:8000/health

# Generate embeddings
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-Embedding-4B",
    "input": "Hello, world!",
    "dimensions": 1024
  }'
```

## Usage Examples

### Basic Python Client

```python
import httpx
import asyncio

async def get_embedding(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": text,
                "dimensions": 1024
            }
        )
        result = response.json()
        return result["data"][0]["embedding"]

# Usage
embedding = asyncio.run(get_embedding("Agent knowledge base"))
print(f"Embedding dimension: {len(embedding)}")
```

### Using the Provided Client

```python
from embedding_client_example import EmbeddingClient

client = EmbeddingClient("http://localhost:8000")

# Single text
embedding = await client.embed("Your text here")

# Batch processing
embeddings = await client.embed([
    "Document 1",
    "Document 2",
    "Document 3"
], dimensions=512)

# Similarity
similarity = await client.similarity(
    "machine learning",
    "artificial intelligence"
)
```

## Integration with Knowledge Base

### Vector Database (e.g., Pinecone, Weaviate, Milvus)

```python
# Generate embeddings for documents
docs = ["doc1 text", "doc2 text", ...]
embeddings = await client.embed(docs, dimensions=1024)

# Store in vector DB
# vector_db.upsert(ids, embeddings, metadata)
```

### Graph Database (e.g., Neo4j)

```python
# Create entity embeddings for semantic node matching
entity_descriptions = [
    "Agent specializing in research",
    "Tool for web scraping",
    "Database for vector storage"
]
entity_embeddings = await client.embed(entity_descriptions)

# Store embeddings as node properties
# graph_db.create_node("Agent", embedding=emb, description=desc)
```

### Hybrid Search (Relational + Vector)

```python
# Metadata in relational DB
# metadata_db.insert(id, type, name, created_at)

# Embeddings in vector DB for semantic search
# vector_db.insert(id, embedding)

# Query: SQL filter + vector similarity
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_REPO` | `Qwen/Qwen3-Embedding-4B` | HuggingFace model repository |
| `EMBEDDING_MODEL_PATH` | `~/.cache/embedding_models/...` | Local model cache path |
| `EMBEDDING_BASE_DIM` | `2560` | Maximum embedding dimension |
| `EMBEDDING_MAX_BATCH_SIZE` | `32` | Maximum texts per request |
| `EMBEDDING_MAX_INPUT_LENGTH` | `8192` | Maximum characters per text |
| `EMBEDDING_REQUEST_TIMEOUT` | `120.0` | Request timeout in seconds |
| `EMBEDDING_HOST` | `0.0.0.0` | Server host |
| `EMBEDDING_PORT` | `8000` | Server port |
| `EMBEDDING_ALLOW_ORIGINS` | `*` | CORS allowed origins |

## Performance Tips

1. **Batch Processing**: Group multiple texts together for better throughput
2. **Dimension Selection**: Use lower dimensions (512-1024) for faster retrieval if full 2560 isn't needed
3. **GPU**: Ensure CUDA is available for 10-50x speedup
4. **Workers**: Run multiple uvicorn workers for concurrent requests
5. **Caching**: Cache embeddings for frequently used texts

## Production Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements_embedding.txt .
RUN pip install -r requirements_embedding.txt

COPY embedding_service.py .

ENV EMBEDDING_HOST=0.0.0.0
ENV EMBEDDING_PORT=8000

EXPOSE 8000

CMD ["python", "embedding_service.py"]
```

### Kubernetes

```yaml
apiVersion: v1
kind: Service
metadata:
  name: embedding-service
spec:
  selector:
    app: embedding
  ports:
    - port: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: embedding-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: embedding
  template:
    metadata:
      labels:
        app: embedding
    spec:
      containers:
      - name: embedding
        image: your-registry/embedding-service:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
```

## API Endpoints

### `POST /v1/embeddings`
Generate embeddings (OpenAI-compatible).

**Request:**
```json
{
  "model": "Qwen/Qwen3-Embedding-4B",
  "input": "text or array of texts",
  "dimensions": 1024,
  "encoding_format": "float"
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.1, 0.2, ...]
    }
  ],
  "model": "Qwen/Qwen3-Embedding-4B",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### `GET /health`
Service health check with metrics.

### `GET /ready`
Kubernetes readiness probe.

### `GET /v1/models`
List available models.

## Troubleshooting

### Model Not Loading
- Check `EMBEDDING_MODEL_PATH` exists and contains model files
- Verify HuggingFace credentials if using private models
- Check disk space for model download (~8GB)

### Out of Memory
- Reduce `EMBEDDING_MAX_BATCH_SIZE`
- Use smaller `dimensions`
- Switch to CPU if GPU memory is insufficient

### Slow Performance
- Ensure GPU is available (`CUDA_VISIBLE_DEVICES`)
- Increase batch size if memory allows
- Use multiple workers

### Connection Errors
- Check firewall rules for port 8000
- Verify `EMBEDDING_HOST` and `EMBEDDING_PORT`
- Check CORS settings if calling from browser

## License

This service is designed for use in agent orchestration platforms with local and remote resources.

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Verify configuration in `.env`
3. Test with provided client examples
4. Review health endpoint for service status
