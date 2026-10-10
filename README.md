# Sorim.AI — Intelligent ITSM Helpdesk

Sorim.AI is an AI-assisted IT service desk prototype for incident analysis, knowledge retrieval, and simulated IT automation.

## Features

- AI-assisted incident categorization, priority, impact, urgency, assignment, and resolution suggestions.
- Knowledge-base question answering using semantic search and source references.
- FAISS vector search with Sentence Transformers embeddings.
- Local language-model inference using Ollama and Qwen2.5 3B.
- Simulated password-reset automation with audit logging.
- Mock software-provisioning requests with request IDs and statuses.
- React employee portal connected to a FastAPI backend.

## Technology Stack

- Frontend: React, Vite, JavaScript, CSS
- Backend: Python, FastAPI
- Language model: Qwen2.5 3B through Ollama
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Vector search: FAISS
- Database: MySQL
- API documentation: FastAPI Swagger UI

## Prerequisites

Install Node.js, Python, MySQL, and Ollama.

Download the model before running the application:

    ollama pull qwen2.5:3b

Ensure MySQL is running and the `sorim_itsm` database and required tables are configured for the backend.

## Run the Backend

From the project root:

    source .venv/bin/activate
    cd backend
    python -m uvicorn main:app --reload --port 8000

API documentation:

    http://127.0.0.1:8000/docs

## Run the Frontend

Open a second terminal:

    cd frontend
    npm install
    npm run dev

Open the local URL printed by Vite, typically:

    http://localhost:5173

## Knowledge Base and RAG

Knowledge documents are stored in `backend/knowledge_base/`.

The application splits documents into text chunks, creates normalized sentence-transformer embeddings, and indexes them with FAISS. A user question is matched against relevant chunks. Retrieved content is passed to the language model to produce a grounded response, and the application displays source filenames.

## Demo Scenarios

1. Submit a VPN connectivity incident and inspect the classification and priority.
2. Run the mock password-reset endpoint and inspect its simulated result and audit record.
3. Ask how to troubleshoot Outlook synchronization and inspect the returned source.
4. Request Visual Studio Code through the software-request form and inspect the request ID.
5. Ask an unrelated question to evaluate whether the application declines unsupported answers or offers escalation.

## Database and Integrations

This prototype uses a local MySQL database for incident records, automation audit logs, and software requests.

ServiceNow is not configured. Incident creation and provisioning are demonstrated using local database records and mock workflows rather than a live ServiceNow instance.

Password-reset and software-provisioning actions are simulations. They do not modify real accounts or install software.

## Limitations

- AI classifications and suggested resolutions may be incorrect and require human review.
- The knowledge base contains demonstration documents, not an organization's complete IT policies.
- This prototype is intended for local demonstration, not production deployment.
- Authentication, authorization, production-grade secrets management, and real enterprise integrations require further implementation.
- The current database is MySQL; MongoDB Atlas is not configured.

## Security

Do not commit `.env` files, database passwords, API keys, or other secrets. Use environment variables for credentials before sharing or deploying the project.

## Repository Structure

    backend/       FastAPI endpoints, database access, RAG, and mock automation
    frontend/      React employee portal
    knowledge/     Additional project knowledge files
    tests/         Test-related files
