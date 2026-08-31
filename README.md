# MultiDoc RAG: Enterprise Open-Source Multimodal Document Assistant

An offline, open-source AI document assistant powered by **Hugging Face models** for multi-type content extraction (text, images, tables, graphs, equations) and grounded retrieval-augmented generation (RAG).

---

## 🤖 Extractor Architecture & Open-Source Models

Each extractor in the system utilizes a **distinct, specialized open-source model and pipeline**:

| Extractor Agent | Model / Engine Used | Role & Functionality |
| :--- | :--- | :--- |
| **Text & Layout Extractor** | `PyMuPDF` Layout Engine + OCR Stream | Clean paragraph parsing, word counting, hierarchical document layout structuring. |
| **Image Extractor** | `Salesforce/blip-image-captioning-large` (HF Vision API) | Visual image extraction, zero-black-box PIL alpha compositing, semantic image captioning. |
| **Graphs & Visuals Extractor** | PyMuPDF High-DPI Diagram Crop + Schematic Analyzer | Visual diagram & chart cropping, axis mapping, sequence & workflow analysis. |
| **Table Extractor** | `pdfplumber` + High-DPI Table Image Crop | **Visual table image crop** + **Structured HTML tables** with aligned columns & markdown copy. |
| **Equation Extractor** | Dynamic LaTeX Math Equation Parser | Parses numbered equations, integrals, summations, fractions, and renders standard LaTeX math (`$$...$$`). |
| **Numerical Extractor** | Regex Units & Specification Engine | Extracts numerical tolerances, limits, operating bands, and context sentences. |
| **Dense Vector Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dimensional dense semantic vectors with Cosine / L2 distance search. |
| **Chatbot & RAG Assistant** | `Qwen/Qwen2.5-7B-Instruct` (Hugging Face API Router) | Conversational, direct, grounded answering matching user phrasing and intent. |

---

## 📊 Hugging Face API Calls & Token Consumption Breakdown

Here is the exact accounting of Hugging Face API calls and estimated token consumption for a typical user workflow:

### 1. Document Extraction Pass (Per Uploaded Document)
- **Image Captioning (`Salesforce/blip-image-captioning-large`):**
  - **API Calls:** 1 network call per extracted image/figure (typically 1–6 calls per document).
  - **Payload Size:** ~150–300 KB raw image bytes per call.
  - **Generated Output:** ~30–50 tokens per image description.
- **Local Extractions (Zero External API Tokens Consumed):**
  - Text, Table Image Crops, Structured HTML Tables, Numerical Units, and Dynamic LaTeX Equations are processed locally on the server via PyMuPDF, pdfplumber, and regex parser, consuming **0 Hugging Face API calls/tokens**.
- **Dense Vector Embeddings (`all-MiniLM-L6-v2`):**
  - Handled locally via `sentence-transformers` in Python, consuming **0 HF API quota**.

### 2. Chatbot Conversation Turn (Per User Query)
- **Model:** `Qwen/Qwen2.5-7B-Instruct` via Hugging Face Router API (`https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-7B-Instruct`).
- **API Calls:** **1 call per user message**.
- **Input Context Tokens:** ~350 – 800 tokens (grounded multimodal evidence chunks from the vector database + chat history).
- **Output Response Tokens:** ~150 – 350 tokens (direct, structured answer + cited sources + table/equations).
- **Total per Chat Query:** ~500 – 1,150 tokens.

---

## 🚀 Getting Started

### 1. Environment Setup
Rename `.env.example` to `.env` (or verify `backend/.env`):
```bash
HUGGINGFACE_API_KEY=hf_YourHuggingFaceTokenHere
TEXT_GENERATION_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
IMAGE_MODEL=Salesforce/blip-image-captioning-large
```

### 2. Start Backend API Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Start Frontend Client
```bash
cd frontend
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

## 🔒 Security & Privacy

- **Password Hashing:** Passwords hashed with `bcrypt` / PBKDF2 (never plaintext or reversibly encrypted).
- **Session Privacy:** User document chunks and conversation queries are isolated by user IDs in the SQLite database and vector index.
- **Zero Paid Dependencies:** No reliance on OpenAI, Anthropic, or paid commercial APIs.
