# VERICLAIM Architecture

The project is structured as a monorepo with the following main components:

- **frontend/**: React + Vite + TypeScript application
- **backend/**: FastAPI application for NLP pipeline and API
- **data/**: Storage for raw and processed PDF documents
- **models/**: Local storage for downloaded HF models
- **notebooks/**: Jupyter notebooks for experiments and EDA

## Backend Architecture
- **api/**: FastAPI routes
- **core/**: App configuration, security, etc.
- **models/**: SQLAlchemy database models
- **schemas/**: Pydantic models for request/response validation
- **services/**: Core business logic
- **nlp/**: NLP logic (claim extraction, NLI, etc.)
- **retrieval/**: FAISS and similarity search
- **verification/**: The final decision engine
- **document_processing/**: PDF parsing logic
- **database/**: Database connection and session management
