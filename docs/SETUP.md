# Local Setup and Deployment

## Prerequisites

- Python installed for the backend services. `Content-Processing-Agent/.python-version` specifies Python 3.13.
- Node.js and npm for the Next.js frontend.
- A configured SQL database for Orchestrator database features.
- API credentials for any external providers you enable.

## Independent Python environments

Each service has its own requirements file. Create one virtual environment per service and install dependencies from that service's directory.

### Orchestrator

```bash
cd Orchestrator_Agent
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Content Processing Agent

```bash
cd Content-Processing-Agent
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Educational Agent

```bash
cd Educational-Content-Generator-Agent/backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Multimedia Agent

Run from the `Multimedia-Agent` directory:

```bash
cd Multimedia-Agent
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8003
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment variables

Use `.env.example` as a starting point. Place variables in the service directory that reads them. The exact `.env` loading location should be confirmed in each service's configuration module. Never commit actual credentials.

Core URL settings:

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Frontend API gateway URL |
| `NEXT_PUBLIC_MULTIMEDIA_URL` | Frontend multimedia URL |
| `CONTENT_PROCESSING_URL` | Content Processing service URL used by Orchestrator |
| `CONTENT_PROCESSING_AGENT_URL` | Content Processing service URL used by Educational Agent |
| `EDUCATIONAL_AGENT_URL` | Educational Agent URL used by Orchestrator |
| `MULTIMEDIA_AGENT_URL` | Multimedia Agent URL used by Orchestrator |
| `DATABASE_URL` | SQLAlchemy database connection |
| `JWT_SECRET_KEY` | Authentication signing secret |
| `FRONTEND_URL` | CORS frontend origin |

## Deployment checklist

- Deploy each backend as its own service with the correct root directory and start command.
- Deploy the frontend separately.
- Configure service URLs to point to deployed services.
- Set provider keys and database credentials in the hosting platform's secret/environment settings.
- Add the deployed frontend origin to backend CORS allowlists.
- Ensure generated output directories are writable and persistent if generated files must survive restarts.
- Test authentication, chat, quiz, flashcards, diagram, and multimedia routes individually and then through the frontend.
- Verify all external provider quotas and permissions.
