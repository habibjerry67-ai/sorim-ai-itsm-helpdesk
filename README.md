# Sorim.AI — Intelligent ITSM Helpdesk

Sorim.AI is an AI-assisted IT service management (ITSM) helpdesk prototype that combines AI-powered incident analysis, semantic knowledge retrieval, safe self-healing decisions, and ServiceNow incident integration.

The application provides an employee-facing React portal backed by a FastAPI service, MySQL database, and locally hosted language model.

## Features

- **AI-assisted incident analysis:** Categorizes incidents and suggests priority, impact, urgency, escalation requirements, and resolutions.
- **Knowledge-base question answering:** Retrieves relevant troubleshooting information using semantic search and displays source references.
- **Retrieval-Augmented Generation (RAG):** Uses Sentence Transformers embeddings and FAISS vector search to retrieve relevant knowledge-base content.
- **Local AI inference:** Uses Ollama with the Qwen2.5 3B model.
- **Self-healing workflow:** Identifies reported issues, diagnoses possible causes, retrieves relevant knowledge, and decides whether to provide guidance, require identity verification, or escalate to a human.
- **ServiceNow integration:** Creates incidents in a configured ServiceNow instance for incident analysis and self-healing workflows.
- **Simulated password-reset automation:** Demonstrates a password-reset workflow with audit logging without changing a real password.
- **Software provisioning requests:** Generates request IDs and records simulated request statuses without installing software.
- **Employee portal:** Provides interfaces for reporting issues, searching the knowledge base, requesting software, and viewing tickets.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Language model | Qwen2.5 3B through Ollama |
| Embeddings | Sentence Transformers — `all-MiniLM-L6-v2` |
| Vector search | FAISS |
| Database | MySQL |
| ITSM integration | ServiceNow REST API |
| API documentation | FastAPI Swagger UI |

## Prerequisites

Install the following software before running the application:

- Python
- Node.js and npm
- MySQL
- Ollama

Download the language model:

```bash
ollama pull qwen2.5:3b
```

Ensure MySQL is running and the `sorim_itsm` database and required tables are configured.

### Environment configuration

Create a local `.env` file in the project root and configure the required database and ServiceNow settings.

Example configuration:

```dotenv
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=sorim_itsm

SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your_servicenow_username
SERVICENOW_PASSWORD=your_servicenow_password
```

Replace the example values with your own credentials. Never commit the actual `.env` file or credentials to GitHub.

## Run the Backend

From the project root, activate the Python virtual environment and start FastAPI:

```bash
source .venv/bin/activate
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API documentation is available at:

- http://127.0.0.1:8000/docs

The health endpoint is available at:

- http://127.0.0.1:8000/api/health

Keep the backend terminal running.

## Run the Frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically:

- http://localhost:5173

The frontend communicates with the FastAPI backend running on port `8000`.

## Knowledge Base and RAG

Knowledge-base documents are stored in `backend/knowledge_base/`.

The retrieval workflow:

1. Loads the available troubleshooting documents.
2. Splits the documents into text chunks.
3. Generates normalized embeddings using Sentence Transformers.
4. Stores the embeddings in a FAISS index.
5. Retrieves relevant chunks for a user's question.
6. Uses the retrieved information to support the response.
7. Returns relevant source filenames for reference.

The knowledge base contains demonstration troubleshooting material for common IT issues, including VPN connectivity, password problems, Outlook synchronization, Wi-Fi, and printer issues.

## Self-Healing Workflow

The self-healing component demonstrates a controlled approach to resolving IT support issues.

1. **Issue identification:** Determines the likely issue category from the reported problem.
2. **Diagnosis:** Produces a preliminary explanation of the possible cause.
3. **Knowledge retrieval:** Searches the knowledge base for relevant troubleshooting information.
4. **Decision-making:** Selects guided troubleshooting, identity verification, or human escalation according to the issue.
5. **Controlled execution:** Demonstrates simulated actions where appropriate.
6. **Validation:** Records the simulated outcome.
7. **Audit and ITSM integration:** Records the workflow and attempts to create a corresponding ServiceNow incident when configured.

### Safety considerations

- Password-reset actions are simulated and do not change real passwords.
- Identity verification in this prototype is not a production-grade identity verification mechanism.
- Unrecognized or sensitive issues should be escalated rather than automatically acted upon.
- AI-generated diagnoses and decisions require appropriate human oversight.

## ServiceNow Integration

The application supports creating incidents through the ServiceNow Table API when valid credentials and instance configuration are available.

The integration can include incident details such as:

- Short description
- Detailed issue description
- Category
- Impact and urgency
- Self-healing case ID and workflow outcome, where applicable

The self-healing workflow reports the ServiceNow creation result so that the user can inspect the associated incident.

**Note:** ServiceNow incident creation requires a reachable instance, valid credentials, and the appropriate API permissions. The integration does not guarantee that every request will succeed.

## Demo Scenarios

Use the following scenarios to demonstrate the application's capabilities:

1. **Incident analysis:** Submit a VPN connectivity issue and inspect the suggested classification, priority, and resolution.
2. **Knowledge retrieval:** Ask how to troubleshoot Outlook synchronization and inspect the returned sources.
3. **Self-healing — VPN:** Submit a VPN issue and inspect the guided troubleshooting decision and ServiceNow incident result.
4. **Self-healing — expired password:** Submit a password-expiration issue and verify that the workflow requests identity verification instead of performing a real password reset.
5. **Self-healing — unknown issue:** Submit an unrecognized issue and inspect the escalation decision.
6. **Software request:** Request Visual Studio Code and inspect the generated request ID and simulated status.
7. **Ticket tracking:** Open My Tickets and inspect locally stored incident records.

## Database

MySQL stores the application's local incident records and the database-backed records used by supported audit, self-healing, and software-request workflows.

The database schema must be initialized before running the relevant features. ServiceNow incidents are created separately through the configured ServiceNow API.

## Repository Structure

```text
itsm-helpdesk/
├── backend/
│   ├── knowledge_base/
│   ├── main.py
│   ├── self_heal.py
│   ├── servicenow_client.py
│   ├── rag.py
│   ├── automation.py
│   └── provisioning.py
├── frontend/
│   └── src/
├── .gitignore
└── README.md
```

This is a high-level overview; additional files may be present in the repository.

## Limitations

- This is a prototype intended for demonstration, not production deployment.
- AI classifications, diagnoses, and suggested resolutions may be incorrect.
- The knowledge base contains demonstration documents and may not cover every organization-specific IT policy.
- Password-reset and software-provisioning workflows are simulated.
- Production deployment requires robust authentication, authorization, identity verification, monitoring, and secrets management.
- The current database is MySQL; MongoDB Atlas is not configured.
- ServiceNow functionality depends on the configured instance, credentials, permissions, and network connectivity.

## Security

- Never commit `.env` files, database passwords, API keys, or ServiceNow credentials.
- Store credentials in environment variables or an appropriate secrets manager.
- Rotate any credentials that may have been exposed.
- Review Git history for previously committed secrets before making the repository public.
- Do not expose internal service credentials or sensitive incident information in screenshots or documentation.

## Future Improvements

- Integrate a production-grade identity provider for verified user identity.
- Add role-based access control.
- Improve retrieval relevance and knowledge-base coverage.
- Add automated tests for API endpoints and self-healing decisions.
- Expand monitoring, audit reporting, and error handling.
- Integrate real enterprise automation only with appropriate authorization and safeguards.

---

**Sorim.AI** — AI-assisted IT support with knowledge retrieval, controlled self-healing decisions, and ITSM integration.
