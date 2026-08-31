# System Architecture Documentation

## Universal Multimodal RAG Multi-Agent Document Intelligence Assistant

### 1. High-Level Architecture Overview

The system implements a decoupled, modular full-stack architecture consisting of an ASGI FastAPI backend, an SQLite relational metadata layer, a dense-sparse hybrid vector index (FAISS/Cosine Store + BM25-style keyword matching), an 8-agent multi-agent coordination orchestrator, and a 15-page React frontend.

```
+---------------------------------------------------------------------------------------------------+
|                                      REACT FRONTEND (15 Pages)                                    |
| Login | 2-Step Auth | Dashboard | Upload | Library | Assistant | Evidence | Agents | Activity     |
| Explorer | Image/Table Viewer | Evaluation | System Health | Settings | Help | Light/Dark Theme   |
+-------------------------------------------------+-------------------------------------------------+
                                                  | REST API (Axios / Fetch + JWT)
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                      FASTAPI BACKEND & ORCHESTRATOR                                |
|  Routes: /api/auth | /api/documents | /api/query | /api/agents | /api/evaluation | /api/system    |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                 +--------------------------------+--------------------------------+
                 |                                                                 |
                 v                                                                 v
+------------------------------------+           +-------------------------------------------------+
|      DOCUMENT INGESTION AGENTS     |           |          QUERY & INFERENCE AGENTS               |
| 1. Document Processing Agent       |           | 5. Query Understanding Agent (Intent/Modality)  |
|    - PyMuPDF, python-docx, pandas  |           | 6. Retrieval Agent (FAISS + BM25/TF-IDF Hybrid) |
| 2. Image Understanding Agent       |           | 7. Evidence Validation Agent (Contradictions)   |
|    - Vision captioning & OCR       |           | 8. RAG Answer Agent (Strict grounded answers)   |
| 3. Table Understanding Agent       |           | 9. Response Verification Agent (Hallucination)  |
| 4. Embedding & Chunking Pipeline   |           +-------------------------------------------------+
+-----------------+------------------+                                             |
                  |                                                                v
                  v                                              +----------------------------------+
+------------------------------------+                           |        HUGGING FACE / LOCAL      |
|     STORAGE & VECTOR DATABASE      |                           |   - Text Gen: Mistral / Zephyr   |
| - SQLite: Users, Docs, Activity    |<--------------------------|   - Embeddings: BAAI / MiniLM    |
| - FAISS: Dense Multimodal Vectors  |                           |   - Vision: BLIP / ViT / OCR     |
| - Inverted Index: Keyword BM25     |                           |   - Graceful Offline Fallback    |
+------------------------------------+                           +----------------------------------+
```

---

### 2. Ingestion Pipeline Mechanics

When a document (PDF, DOCX, CSV, XLSX, PNG, JPG) is uploaded:
1. **Document Processing Agent** identifies file extension and parses the file structure:
   - For PDFs, **PyMuPDF (`fitz`)** extracts per-page plain text, page coordinates, and renders page preview thumbnails.
   - Embedded raster images are extracted from xref tables and passed to **Image Understanding Agent**.
   - Tables are extracted via **`pdfplumber`** and passed to **Table Understanding Agent**.
2. **Table Understanding Agent** transforms 2D matrix grids into Markdown format and builds natural language assertions for each row:
   ```text
   In table on page 3 (Specifications):
   Row 1 (Parameter: Spindle Speed, Nominal: 8,000-12,000 RPM, Critical: 16,000 RPM)
   ```
3. **Image Understanding Agent** analyzes aspect ratios, visual diagrams, schematics, and calls Hugging Face Vision API (`Salesforce/blip-image-captioning-large`) or deterministic domain visual synthesis.
4. **Chunk Service** bundles text, tables, and image descriptions into chunks preserving metadata:
   ```json
   {
     "document_id": 1,
     "page_number": 4,
     "content_type": "table",
     "domain": "Manufacturing",
     "content_text": "..."
   }
   ```
5. **Embedding Service** computes normalized 384-dimensional dense vectors and commits them to the vector index.

---

### 3. Hybrid Dense-Sparse Retrieval Mechanics

Standard dense vector search often struggles with specific technical codes (e.g. `ERR-04`), acronyms (`CAPEX`), or numerical limits (`210 bar`). Our hybrid retrieval balances semantic understanding and keyword matching:

$$\text{Score}_{\text{hybrid}} = \left( 0.7 \times \text{Score}_{\text{dense}} + 0.3 \times \text{Score}_{\text{sparse}} \right) \times \text{ModalityBoost}$$

- **Dense Cosine Similarity:** Inner product of normalized query and chunk vectors.
- **Sparse Keyword Overlap:** BM25-inspired term frequency matching against query keywords.
- **Modality Boost ($1.25\times$):** Applied when query keywords indicate a specific modality (e.g., "table", "diagram", "schematic").

---

### 4. Database Schema

The SQLite database manages 10 relational tables:
- `users`: User authentication, hashed passwords, 2FA secret codes.
- `documents`: Document filename, size, domain, status, and summary counts.
- `document_pages`: Page numbers, raw extracted text, and thumbnail paths.
- `document_chunks`: Indexed chunk text, modality, token counts, and metadata.
- `document_images`: Extracted figure paths, bounding dimensions, and AI captions.
- `document_tables`: Raw Markdown, JSON rows/cols, and natural language assertions.
- `query_records`: Queries, intent, modality, grounded answers, confidence, and groundedness ratings.
- `query_evidence`: Candidate chunks, individual score breakdowns (semantic, keyword, hybrid).
- `agent_status`: Live 8-agent registry, state, tasks executed, and latency.
- `agent_activity_logs`: Chronological telemetry audit trail with trace IDs.
- `evaluation_runs` & `evaluation_items`: Empirical benchmark runs and metric scores.
