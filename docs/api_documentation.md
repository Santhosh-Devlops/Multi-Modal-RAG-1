# REST API Documentation

Base URL: `http://localhost:8000`

---

## 1. Authentication Endpoints

### `POST /api/auth/register`
Register a new student or demo account.
- **Request Body:**
  ```json
  {
    "email": "user@university.edu",
    "password": "password123",
    "full_name": "Jane Doe"
  }
  ```
- **Response (200):**
  ```json
  { "status": "success", "message": "User registered successfully" }
  ```

### `POST /api/auth/login`
First step authentication.
- **Request Body:**
  ```json
  { "email": "student@university.edu", "password": "internship2026" }
  ```
- **Response (200):**
  ```json
  {
    "status": "2fa_required",
    "email": "student@university.edu",
    "temp_token": "eyJhbGciOi...",
    "demo_hint_code": "123456"
  }
  ```

### `POST /api/auth/verify-2fa`
Second step authentication completing 2FA challenge.
- **Request Body:**
  ```json
  {
    "email": "student@university.edu",
    "temp_token": "eyJhbGciOi...",
    "code": "123456"
  }
  ```
- **Response (200):**
  ```json
  {
    "status": "success",
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": 1, "email": "student@university.edu", "role": "student" }
  }
  ```

---

## 2. Document Endpoints

### `POST /api/documents/upload`
Upload a document (PDF, DOCX, CSV, XLSX, PNG, JPG).
- **Form Data:**
  - `file`: Multipart binary file
  - `domain`: `"Manufacturing" | "Healthcare" | "Finance" | ...`
  - `doc_type`: `"Equipment Operations & Maintenance Manual"`

### `GET /api/documents`
List all ingested documents.
- **Query Params:** `domain`, `status`, `doc_type`

### `GET /api/documents/{doc_id}`
Retrieve full details, page list, images, and tables for a document.

### `DELETE /api/documents/{doc_id}`
Purge document metadata and remove all associated vectors from index.

### `POST /api/documents/{doc_id}/reprocess`
Reprocess and re-index an existing document.

---

## 3. Query & RAG Assistant Endpoints

### `POST /api/query`
Execute the multi-agent multimodal RAG pipeline.
- **Request Body:**
  ```json
  {
    "question": "What is the maximum operating temperature in the table?",
    "domain": "Manufacturing",
    "document_id": null,
    "top_k": 5
  }
  ```
- **Response (200):**
  ```json
  {
    "status": "success",
    "result": {
      "query_id": 1,
      "trace_id": "trace_a1b2c3d4e5",
      "question": "What is the maximum operating temperature in the table?",
      "intent": "Numerical Lookup & Parameter Check",
      "requested_modality": "Tabular / Matrix Data",
      "answer": "According to industrial_cnc_machining_manual.pdf [Page 3], ...",
      "confidence_score": 0.94,
      "groundedness_score": 0.96,
      "sources": [
        {
          "source_index": 1,
          "document_id": 1,
          "document_name": "industrial_cnc_machining_manual.pdf",
          "page_number": 3,
          "content_type": "table",
          "hybrid_score": 0.92
        }
      ],
      "verification_status": "Verified Grounded (No Hallucination)",
      "execution_time_ms": 142.5
    }
  }
  ```

---

## 4. Agent & Telemetry Endpoints

### `GET /api/agents`
List all 8 agents and their live status.

### `GET /api/agents/activity`
Retrieve real-time audit logs of agent operations and latencies.

---

## 5. Evaluation & System Endpoints

### `GET /api/evaluation/benchmark`
Get benchmark dataset questions.

### `POST /api/evaluation/run`
Execute automated benchmark evaluation across all documents.

### `GET /api/system/health`
Live ping check of API, SQLite, Vector Store, Embedding Engine, and Model API.

### `GET /api/system/stats`
Aggregated dashboard statistics.
