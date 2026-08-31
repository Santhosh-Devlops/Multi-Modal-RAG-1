# Multi-Agent Design & Specification

## 8 Specialized Autonomous Agents

The system avoids "agent-washing" by strictly assigning distinct, non-overlapping input/output contracts to 8 specialized agents.

---

### Agent 1: Document Processing Agent
- **Key:** `document_agent`
- **Role:** Coordinates multi-format file ingestion, structural parsing, page text extraction, and hands off visual/tabular assets to specialized agents.
- **Input:** Multi-page PDF, DOCX, CSV, XLSX, PNG, JPG files.
- **Output:** Structured pages, metadata, and coordinated vector indexing.

---

### Agent 2: Image Understanding Agent
- **Key:** `image_agent`
- **Role:** Analyzes raster diagrams, schematics, flowcharts, and technical figures extracted from documents to generate semantic visual captions.
- **Input:** Raster image files, visual bounding boxes, page context text.
- **Output:** Visual diagram type classification, technical description, and multimodal chunk vectors.

---

### Agent 3: Table Understanding Agent
- **Key:** `table_agent`
- **Role:** Extracts row and column matrices from tabular sections, generates clean Markdown tables, and formulates natural-language assertions.
- **Input:** PDF tabular bounding boxes, CSV datasets, Excel spreadsheets.
- **Output:** Markdown matrix representations and queryable natural-language assertions.

---

### Agent 4: Retrieval Agent
- **Key:** `retrieval_agent`
- **Role:** Receives the user question, generates query embeddings, searches the vector index, calculates BM25 term overlap, applies domain filters, and ranks candidate evidence.
- **Input:** User question, domain filter, modality target, Top-K depth.
- **Output:** Ranked evidence chunks with score breakdowns (Semantic, Keyword, Hybrid).

---

### Agent 5: Query Understanding Agent
- **Key:** `query_agent`
- **Role:** Performs semantic classification on the user query to determine user intent, requested modality, domain focus, and numerical requirements.
- **Input:** Raw natural language question.
- **Output:** Intent classification (e.g. Numerical Lookup), target modality (Text, Table, Image, Cross-Modal), and domain.

---

### Agent 6: Evidence Validation Agent
- **Key:** `evidence_agent`
- **Role:** Validates candidate evidence pool, filters low-confidence noise, detects contradictions across multiple sources, and computes corroboration confidence.
- **Input:** Ranked candidate evidence pool.
- **Output:** Clean, corroborated evidence chunks and aggregate evidence confidence score.

---

### Agent 7: RAG Answer Agent
- **Key:** `answer_agent`
- **Role:** Synthesizes strictly grounded answers using ONLY verified evidence sources, enforcing zero-hallucination policies and formatting inline clickable citations `[Doc: Page]`.
- **Input:** User query and validated evidence context.
- **Output:** Grounded answer text with verifiable citation objects.

---

### Agent 8: Response Verification Agent
- **Key:** `verification_agent`
- **Role:** Cross-examines generated answer against input evidence chunks to verify factual alignment, citation correctness, and absence of hallucinated claims.
- **Input:** Generated answer text and supporting evidence chunks.
- **Output:** Groundedness score (0.0 to 1.0) and verification verdict ("Verified Grounded").
