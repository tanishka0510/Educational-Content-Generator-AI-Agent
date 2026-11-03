# API Reference

This is a route inventory extracted from the FastAPI route declarations in the repository. For exact schemas and authentication requirements, run the service and use its Swagger UI at `/docs`.

## Orchestrator (default port 8000)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Gateway status |
| POST | `/signup` | Account registration |
| POST | `/login` | Login |
| GET | `/me` | Current-user information |
| POST | `/process-content` | Chat/content workflow |
| POST | `/chats/session` | Create chat session |
| GET | `/chats` | List chat sessions |
| GET | `/chats/{session_id}` | Read a session |
| PATCH | `/chats/{session_id}` | Update a session |
| DELETE | `/chats/{session_id}` | Delete a session |
| POST | `/quiz/generate` | Generate quiz |
| POST | `/quiz/submit` | Submit quiz |
| GET | `/quiz/history` | Quiz history |
| POST | `/flashcards/generate` | Generate flashcards |
| POST | `/flashcards/submit` | Submit flashcards |
| GET | `/flashcards/history` | Flashcard history |
| POST | `/flashcards/attempt` | Record attempt |
| GET | `/flashcards/attempts` | List attempts |
| GET | `/analytics` | Analytics |
| GET | `/csv` | CSV report |
| GET | `/pdf` | PDF report |
| GET | `/study-plan` | Study plan |
| GET | `/study-plan/pdf` | Study-plan PDF |
| POST | `/qa` | Voice/question-answer endpoint |

The upload router declares `POST /` and document list/delete routes. Check `Orchestrator_Agent/api/upload.py` for its full prefix and schema.

## Content Processing Agent (default port 8001)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service status |
| GET | `/health` | Health check |
| GET | `/detect-subject` | Subject detection |
| POST | `/ask` | Question answering |
| POST | `/process-content` | Content/question processing |
| POST | `/upload/` | Upload |
| POST | `/quiz/retrieve` | Quiz retrieval |
| POST | `/search/` | Search |
| POST | `/retrieve/` | Retrieval |

## Educational Content Generator Agent (default port 8002)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service status |
| POST | `/chat` | Educational chat |
| POST | `/upload` | Upload endpoint |
| POST | `/generate` | Quiz generation (confirm any router prefix in live Swagger) |
| POST | `/generate` | Flashcard generation (confirm any router prefix in live Swagger) |

The quiz and flashcard routers may define their own prefixes; use the live `/docs` output as the final authority.

## Multimedia Agent (default port 8003)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service status |
| GET | `/health` | Health check |
| POST | `/multimedia/summary` | Summary |
| POST | `/multimedia/tts` | Text-to-speech |
| POST | `/multimedia/stt` | Speech-to-text |
| POST | `/multimedia/ask` | Multimedia question |
| POST | `/multimedia/image` | Image operation |
| POST | `/multimedia/video` | Video operation |
| POST | `/multimedia/process` | Multimedia processing |

## Interactive API documentation

When a service is running, open:

- Orchestrator: `http://localhost:8000/docs`
- Content Processing: `http://localhost:8001/docs`
- Educational Agent: `http://localhost:8002/docs`
- Multimedia Agent: `http://localhost:8003/docs`
