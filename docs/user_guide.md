# User Guide & Navigation Manual

This manual explains how to navigate and use all 15 pages of the application.

---

## 1. Authentication Flow
- **Login (`/login`):** Enter email and password (or click "Continue with Google"). Demo credentials: `student@university.edu` / `internship2026`.
- **Two-Step Verification (`/verify-2fa`):** Enter the 6-digit security code `123456` to receive your JWT bearer token.

---

## 2. Dashboard (`/dashboard`)
- Displays real-time operational counts: Total Documents, Total Pages, Extracted Figures, Parsed Tables, Vector Chunks, Questions Answered, and Groundedness Scores.
- Real-time audit stream of the latest agent actions and execution latencies.

---

## 3. Document Ingestion (`/upload`)
- Drag-and-drop any PDF, DOCX, CSV, XLSX, PNG, or JPG file.
- Select domain metadata (Manufacturing, Healthcare, Finance, Education, Defence, etc.).
- Real-time extraction summary reveals detected page count, raster image count, and table matrices.

---

## 4. Document Library (`/documents`)
- Repository of all indexed documents with filtering by domain and status.
- Actions to view in Document Explorer, reprocess document, or delete document.

---

## 5. Multimodal Assistant (`/assistant`)
- Select knowledge domain and optional document filter.
- Type any question or click one of the pre-loaded multi-domain benchmark prompts.
- View the strictly grounded answer, confidence bar, groundedness rating, and clickable page citations.

---

## 6. Retrieved Evidence (`/evidence`)
- Detailed breakdown of all candidate evidence chunks for any query.
- Inspect Dense Vector Score (70%), Sparse Keyword Score (30%), and final Hybrid Score.

---

## 7. Agents Registry (`/agents`)
- Overview of all 8 specialized agents with input/output contracts, task counts, and latency.
- Visual flowcharts explaining both the Query Answering Flow and the Multimodal Ingestion Flow.

---

## 8. Agent Activity (`/agent-activity`)
- Chronological telemetry audit log showing exact timestamps, execution latencies, input summaries, and output results.

---

## 9. Document Explorer (`/explorer`)
- Side-by-side view: rendered high-resolution PDF page previews alongside raw extracted text, detected visual figures, and structured tables.

---

## 10. Image & Table Viewer (`/multimodal-viewer`)
- Dedicated visual gallery of all extracted diagrams and structured tables across the entire repository.

---

## 11. Evaluation Suite (`/evaluation`)
- Live benchmark runner evaluating 10 multi-domain questions.
- Displays Recall@5, MRR, Hit Rate, Precision@5, Faithfulness, Context Relevance, and Citation Accuracy.

---

## 12. System Health (`/system-health`)
- Live diagnostic ping checks verifying FastAPI API, SQLite DB, Vector Store, Embedding Engine, and Model API status.

---

## 13. Settings (`/settings`)
- Light/Dark theme toggle, Top-K retrieval slider, dense vs keyword weighting tuning, and account information.

---

## 14. Help / About (`/help`)
- Full conceptual guide explaining Multimodal RAG, hybrid retrieval equations, agent design, and evaluator demo scripts.
