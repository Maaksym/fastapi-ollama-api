# FastAPI AI Project

FastAPI AI application that accepts user prompts, generates responses using a local Ollama model, returns the AI response to the user, and stores prompt/response history in PostgreSQL.

## Features

- Send prompts to a local AI model through REST API
- Generate and return AI responses to users
- Local AI inference with Ollama and Qwen2.5 3B
- Store prompts and AI responses in PostgreSQL
- View AI request history
- Limit the number of history records returned
- FastAPI REST API
- Pydantic validation
- Async SQLAlchemy
- Alembic migrations
- Docker Compose
- Docker healthchecks
- Pytest tests
- Swagger documentation

## Tech Stack

* Python 3.14
* FastAPI
* Uvicorn
* Ollama
* Qwen2.5 3B
* PostgreSQL
* SQLAlchemy
* asyncpg
* Alembic
* Docker
* Docker Compose
* Pytest
* HTTPX

## Project Structure

```text
fastapi_ai_project/
├── migrations/
│   └── versions/
├── routers/
│   ├── __init__.py
│   └── ai.py
├── tests/
│   └── test_main.py
├── .dockerignore
├── .env
├── .gitignore
├── alembic.ini
├── config.py
├── database.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── models.py
├── repositories.py
├── requirements.txt
├── schemas.py
└── services.py
```

## Architecture

The main request flow is:

```text
User
→ POST /ai/generate/
→ FastAPI Router
→ Service
→ Ollama
→ AI Response
→ Repository saves prompt + answer
→ PostgreSQL
→ FastAPI returns JSON response to User
```

Main file responsibilities:

```text
main.py
→ creates the FastAPI application

routers/ai.py
→ handles HTTP requests and responses

schemas.py
→ validates API input and output data

services.py
→ communicates with Ollama

repositories.py
→ reads and writes database records

models.py
→ describes SQLAlchemy database models

database.py
→ creates database engine and sessions

config.py
→ loads configuration from environment variables

migrations/
→ contains Alembic database migrations
```

## API Endpoints

### Health Check

```http
GET /health/
```

Example response:

```json
{
  "status": "ok"
}
```

### Generate AI Response

```http
POST /ai/generate/
```

Example request:

```json
{
  "prompt": "Що таке FastAPI?"
}
```

Example response:

```json
{
  "prompt": "Що таке FastAPI?",
  "answer": "FastAPI — це сучасний Python-фреймворк для створення API."
}
```

The generated prompt and answer are stored in PostgreSQL.

### AI Request History

```http
GET /ai/history/?limit=5
```

The `limit` query parameter controls how many recent records are returned.

Default:

```text
10
```

Minimum:

```text
1
```

Maximum:

```text
100
```

Example response:

```json
[
  {
    "id": 1,
    "prompt": "Що таке FastAPI?",
    "answer": "FastAPI — це сучасний Python-фреймворк для створення API.",
    "created_at": "2026-08-12T11:45:34.868047"
  }
]
```

## Ollama

Install Ollama and download the model:

```bash
ollama run qwen2.5:3b
```

Check installed models:

```bash
ollama list
```

Ollama normally runs locally on:

```text
http://localhost:11434
```

When FastAPI runs inside Docker, Docker Compose uses:

```text
http://host.docker.internal:11434
```

to access Ollama running on the host machine.

## Environment Variables

Create a `.env` file in the project root.

Example for local development:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/fastapi_ai
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

Do not commit `.env` to GitHub.

Docker Compose overrides the database and Ollama addresses required inside the FastAPI container.

## Run With Docker

Make sure:

* Docker Desktop is running
* Ollama is running
* `qwen2.5:3b` is installed

Build and start the application:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

Expected result:

```text
fastapi_ai_app   healthy
fastapi_ai_db    healthy
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health/
```

Stop containers:

```bash
docker compose down
```

## PostgreSQL

PostgreSQL runs inside Docker.

Host port:

```text
5433
```

Container port:

```text
5432
```

Connect manually:

```bash
docker exec -it fastapi_ai_db psql -U postgres -d fastapi_ai
```

View stored AI requests:

```sql
SELECT * FROM ai_requests;
```

Exit PostgreSQL:

```text
\q
```

## SQLAlchemy

The project uses asynchronous SQLAlchemy.

`database.py` creates:

```text
engine
→ connection mechanism to PostgreSQL

AsyncSessionLocal
→ factory for database sessions

get_db()
→ provides a database session to FastAPI endpoints
```

## Alembic Migrations

Alembic manages database schema changes.

Check the current migration:

```bash
alembic current
```

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Docker automatically runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

## Tests

Run tests:

```bash
python -m pytest
```

Tests currently verify:

* health endpoint
* successful AI endpoint behavior
* empty prompt validation
* missing prompt validation
* prompt maximum length
* AI service failure handling
* HTTP status codes
* response JSON

External Ollama calls are replaced with fake responses in unit tests using `monkeypatch`.

## Validation

Prompt requirements:

```text
minimum length: 1 character
maximum length: 1000 characters
```

Invalid input returns:

```text
422 Unprocessable Entity
```

If the AI service is unavailable:

```text
502 Bad Gateway
```

If the AI request exceeds the configured timeout:

```text
504 Gateway Timeout
```

## Docker Services

The project uses two Docker services:

```text
app
→ FastAPI application

db
→ PostgreSQL database
```

The FastAPI container waits until PostgreSQL becomes healthy before starting.

Both services have Docker healthchecks.

## Swagger

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

From Swagger you can test:

```text
GET /health/

POST /ai/generate/

GET /ai/history/
```

## Security

The `.env` file is ignored by Git and should never be committed.

The project `.gitignore` should include:

```text
.venv/
.env
__pycache__/
*.pyc
```

The `.dockerignore` should include:

```text
.venv
__pycache__
*.pyc
.env
.git
.pytest_cache
```

## Final Run

To verify the project from a clean Docker start:

```bash
docker compose down
docker compose up -d --build
docker compose ps
```

Then check:

```text
http://127.0.0.1:8000/health/
http://127.0.0.1:8000/docs
```

Test AI generation and prompt history through Swagger.
