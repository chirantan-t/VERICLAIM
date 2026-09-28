# VERICLAIM: Scientific Claim & Citation Verification System

## Problem
Given a research paper containing claims and citations, it is difficult to automatically determine whether the cited evidence actually supports the specific scientific claim being made.

## Motivation
To build a serious academic/research-grade NLP project to verify scientific claims against cited literature, preserving traceability and detecting nuances like numerical discrepancies.

## Architecture
VERICLAIM uses a decoupled architecture:
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **NLP / ML**: Hugging Face Transformers, Sentence Transformers, FAISS (Future phases)

## Pipeline
The core pipeline involves PDF parsing, claim extraction, semantic retrieval, natural language inference (NLI), numerical consistency checks, and a final verification layer.

## Installation & Setup
1. Clone the repository or navigate to this folder.
2. Make sure Docker and Docker Compose are installed.
3. Run `docker-compose up --build`.
4. The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:8000`.

## Current Status (Project Complete - Phases 1 to 11)
- **Phase 1-3:** Scalable API, PDF ingestion, heuristics-based scientific claim extraction, and citation linking.
- **Phase 4-7:** Semantic retrieval via FAISS and `sentence-transformers`, Natural Language Inference for support/contradiction, numerical consistency checking, and final verdict orchestration.
- **Phase 8:** Interactive React frontend for file uploading and verification result visualization.
- **Phase 9-11:** End-to-end evaluation framework, ablation study tools, and comprehensive unit tests.

## Running Tests and Studies
- **Unit Tests:** Run `pytest backend/tests/` to verify components.
- **Ablation Study:** Run `python backend/scripts/run_ablation_study.py` to test the impact of the numerical consistency engine on verdict accuracy.
