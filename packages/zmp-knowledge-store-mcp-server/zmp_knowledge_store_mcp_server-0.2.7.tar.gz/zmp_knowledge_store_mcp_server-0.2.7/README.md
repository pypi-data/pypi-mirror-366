# ZMP Knowledge Store MCP Server

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-knowledge_store_mcp_server-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)

A high-performance backend service for managing knowledge store content, supporting multi-tenant ChromaDB integration, real-time progress tracking, and secure authentication.

---

## Python File Structure

```
zmp_knowledge_store/
├── __init__.py              # Package initialization & metadata
├── config.py                # Configuration management
├── knowledge_store.py       # Main knowledge store logic (ingestion, search, backend selection)
├── qdrant_adapter.py        # Qdrant vector DB integration
├── chromadb_adapter.py      # ChromaDB vector DB integration
├── keyword_extractor.py     # Advanced keyword extraction
├── utils.py                 # Utility functions

tests/
├── test_client.py           # Test client for validation
├── test_mcp_ingest_setup_a_project.py      # Ingestion & search test for setup-a-project example
├── test_mcp_ingest_group_management.py     # Ingestion & search test for group-management example
├── ...                      # Other tests (see tests/ directory)

examples/
├── zcp/getting-started/setup-a-project/
│   ├── setup-a-project.mdx
│   └── *.png (all referenced images)
├── zcp/advanced-guide/security-and-access-control/role-group-and-permissions/
│   ├── group-management.mdx
│   └── *.png (all referenced images)
```

---

## Key Features in the Source Code

### 1. Unified Knowledge Store (`knowledge_store.py`)
- Handles ingestion, chunking, and search for solution documentation
- Supports both Qdrant and ChromaDB as vector stores
- Multi-backend SmolDocling model support (MLX for Apple Silicon, Transformers for cross-platform)
- Robust image and page number assignment logic for MDX/PDF ingestion
- Metadata enrichment and error handling

### 2. Configuration Management (`config.py`)
- Environment-based configuration
- Embedding model and backend selection
- Default values and cluster mode support

### 3. Vector Store Adapters
- `qdrant_adapter.py`: Qdrant integration (search, upsert, collection management)
- `chromadb_adapter.py`: ChromaDB integration (search, upsert, collection management)

### 4. Keyword Extraction (`keyword_extractor.py`)
- Multiple extraction methods (KeyBERT, spaCy, NLTK, custom)
- Solution-specific optimization (ZCP, AMDP, APIM)
- Adaptive keyword counts (5-12 based on content)
- Domain vocabulary and technical term boosting

### 5. Utilities (`utils.py`)
- Chunking, document creation, and helper functions

### 6. Tests & Example Data
- Comprehensive test suite in `tests/` (pytest-based)
- Example ingestion sets in `examples/` for both setup-a-project and group-management

---

## MCP Tools Implemented

| Tool Name           | Request Schema                | Response Schema                        | Description |
|---------------------|------------------------------|----------------------------------------|-------------|
| ingest_documents    | `{documents: list, solution?: str}`   | `{ success: bool, results: list, total_page_count?: int }`              | Ingest documents with metadata and keyword extraction. |
| search_knowledge    | `{query: str, n_results?: int}`       | `{ query: str, results: list }`    | Search the knowledge store for relevant info. |
| log_chat_history    | `{query: str, response: str, user_id?: str, session_id?: str}` | `{ success: bool, id?: str, error?: str }` | Log a user query/response pair to chat history. Deduplication by (query, user_id). |
| search_chat_history | `{query: str, user_id?: str, n_results?: int}` | `{ query: str, user_id?: str, results: list }` | Hybrid search over chat history, filtered by clustering and semantic similarity. |

---

## Usage Examples

```python
# Ingest documents (see examples/ for sample MDX and images)
result = await client.call_tool("ingest_documents", {
    "documents": [...],
    "solution": "zcp"
})

# Search knowledge
result = await client.call_tool("search_knowledge", {
    "query": "Group Management",
    "n_results": 3
})

# Log chat history
result = await client.call_tool("log_chat_history", {
    "query": "What is a group?",
    "response": "A group is ...",
    "user_id": "user1"
})

# Search chat history
result = await client.call_tool("search_chat_history", {
    "query": "Delete a group",
    "n_results": 5
})
```

---

## Example Ingestion Sets

- `examples/zcp/getting-started/setup-a-project/`: MDX and images for "Setup a Project" documentation
- `examples/zcp/advanced-guide/security-and-access-control/role-group-and-permissions/`: MDX and images for "Group Management" documentation

---

## Running the Tests

- All tests are in the `tests/` directory and use `pytest`.
- Key ingestion and search tests:
  - `test_mcp_ingest_setup_a_project.py`: Ingests and verifies the setup-a-project example
  - `test_mcp_ingest_group_management.py`: Ingests and verifies the group-management example
- To run all tests:

```bash
pytest tests/
```

---

## Troubleshooting: Embedding Dimension Mismatch

If you see errors like:

```
Collection expecting embedding with dimension of 384, got 768
```

- This means your embedding model (e.g., `all-mpnet-base-v2`) outputs a different dimension than the collection was created with (e.g., `all-MiniLM-L6-v2`).
- **Solution:** Delete the ChromaDB collection and re-ingest, or update your config to match the expected dimension.

---

## SmolDocling Backend Selection & Platform Compatibility

- The backend for SmolDocling is controlled by the `SMOLDOCLING_BACKEND` environment variable:
  - `mlx`: Use MLX backend (Apple Silicon only)
  - `transformers`: Use HuggingFace Transformers backend (cross-platform)
  - `auto`: Auto-select based on platform
- MLX backend is recommended for Apple Silicon (macOS); Transformers backend is recommended for Linux/Kubernetes or non-Apple hardware.
- See `PLATFORM_COMPATIBILITY.md` for more details.

---

## Environment Configuration

Set the following environment variables in your `.env` file or deployment environment:

(See previous section for full table of variables)

---

## Deployment Guide

### Installation

(Instructions TBD)
