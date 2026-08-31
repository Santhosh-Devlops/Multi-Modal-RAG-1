# Setup & Installation Guide

This guide describes how to set up and run the **Universal Multimodal RAG Assistant** on Windows, Linux, and macOS.

---

## 1. Prerequisites

- **Python:** 3.10, 3.11, or 3.12
- **Node.js:** 18.x or 20.x or 22.x
- **npm:** 9.x or 10.x

---

## 2. Quick Start Commands

### Step 1: Clone or Navigate to Project Directory
```bash
cd "d:/Internship Project"
```

### Step 2: Backend Setup
```bash
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```
Backend API will be running at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

---

### Step 3: Dataset Generation & Seeding (Pre-loads 15-Page Multi-Domain PDFs)
In a new terminal window:
```bash
python dataset/generate_sample_dataset.py
python dataset/seed_database.py
```
This generates authentic 15-page manuals with diagrams and tables for Manufacturing, Healthcare, Finance, Education, and Defence, and indexes them into SQLite and the vector store.

---

### Step 4: Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Frontend development server will be running at: `http://localhost:3000`.

---

## 3. Demo Credentials

- **Email:** `student@university.edu`
- **Password:** `internship2026`
- **2-Step Verification Code:** `123456`
