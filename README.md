# FastAPI AI Support Assistant

A backend AI application built with **FastAPI**, **Ollama**, and **PostgreSQL**. The project started as a simple AI text-generation API and was expanded into a small **AI agent** that can select tools, use persistent memory, run background tasks, and call an external weather API.

The project is designed as a practical backend/AI portfolio project and demonstrates API development, asynchronous database access, Docker, migrations, monitoring, testing, CI/CD, and agent-style workflows.

## Features

- REST API built with FastAPI
- Local AI inference with Ollama and `qwen2.5:3b`
- AI prompt/response history stored in PostgreSQL
- AI agent with tool selection
- Persistent agent memory through saved notes
- Reading saved notes to answer later questions
- Background AI tasks with FastAPI `BackgroundTasks`
- External HTTP API integration with Open-Meteo
- Async SQLAlchemy + asyncpg
- Alembic database migrations
- Pydantic request/response validation
- Docker Compose environment
- Docker healthchecks
- Prometheus metrics
- Grafana dashboards
- Pytest tests
- Swagger / OpenAPI documentation
- GitHub Actions CI pipeline
- Docker image build and push to GitHub Container Registry

## Tech Stack

- Python 3.14
- FastAPI
- Uvicorn
- Ollama
- Qwen2.5 3B
- PostgreSQL
- SQLAlchemy
- asyncpg
- Alembic
- HTTPX
- Docker
- Docker Compose
- Prometheus
- Grafana
- prometheus-fastapi-instrumentator
- Pytest
- GitHub Actions
- GitHub Container Registry (GHCR)
- Open-Meteo API

## Project Structure

```text
fastapi_ai_project/
├── migrations/
│   ├── env.py
│   └── versions/
├── routers/
│   ├── __init__.py
│   ├── ai.py
│   └── agent.py
├── tests/
│   └── test_main.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .dockerignore
├── .env
├── .gitignore
├── agent_service.py
├── agent_tools.py
├── alembic.ini
├── config.py
├── database.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── models.py
├── prometheus.yml
├── repositories.py
├── requirements.txt
├── schemas.py
└── services.py
```

## Architecture

### Standard AI request

```text
User
  ↓
POST /ai/generate/
  ↓
FastAPI Router
  ↓
AI Service
  ↓
Ollama
  ↓
AI Response
  ↓
Repository
  ↓
PostgreSQL
  ↓
JSON response to User
```

### AI agent request

```text
User
  ↓
POST /agent/query/
  ↓
routers/agent.py
  ↓
run_agent()
  ↓
choose_tool()
  ↓
HISTORY / SAVE_NOTE / GET_NOTES / GET_WEATHER / NONE
  ↓
Selected tool or normal AI response
  ↓
JSON response to User
```

The agent uses a hybrid approach: clear commands can be routed by Python rules, while less obvious cases can be classified by the LLM.

## Main File Responsibilities

- `main.py` — creates the FastAPI application, registers routers, exposes health and Prometheus metrics.
- `routers/ai.py` — handles standard AI generation and history HTTP endpoints.
- `routers/agent.py` — handles agent and background-task HTTP endpoints.
- `schemas.py` — defines Pydantic request and response models.
- `services.py` — communicates with the local Ollama API through HTTPX.
- `repositories.py` — contains PostgreSQL read/write operations.
- `agent_service.py` — contains agent orchestration and tool-selection logic.
- `agent_tools.py` — contains tools the agent can execute.
- `models.py` — defines SQLAlchemy database models.
- `database.py` — creates the async SQLAlchemy engine and database sessions.
- `config.py` — loads configuration from environment variables.
- `migrations/` — contains Alembic database migrations.

## AI Agent Tools

The agent currently supports several actions.

### `HISTORY`

Returns recent AI prompt/response history from PostgreSQL.

### `SAVE_NOTE`

Stores a note in the `notes` table so the agent can remember information between separate requests.

Example:

```text
Запам'ятай: клієнта звати Андрій
```

The stored note is cleaned before saving:

```text
клієнта звати Андрій
```

### `GET_NOTES`

Reads recent notes from PostgreSQL and passes them to the AI as context.

Example:

```text
Як звати клієнта?
```

Flow:

```text
Question
  ↓
GET_NOTES
  ↓
PostgreSQL notes
  ↓
AI receives notes + question
  ↓
Generated answer
```

This is the project's persistent agent **memory**.

### `GET_WEATHER`

Uses an external API integration.

Flow:

```text
"Яка погода у Варшаві?"
  ↓
GET_WEATHER
  ↓
AI extracts city name
  ↓
Open-Meteo Geocoding API
  ↓
latitude + longitude
  ↓
Open-Meteo Forecast API
  ↓
current temperature
```

No API key is required for this integration.

### `NONE`

If no tool is needed, the message is sent directly to Ollama and the model generates a normal answer.

## Agent Memory and State

The project demonstrates two different concepts:

**Memory** is persistent information that survives between HTTP requests. In this project, notes are stored in PostgreSQL.

**State** is temporary information used while one agent request is being processed, such as:

```text
message
selected tool
city
notes
result
```

Request state disappears when the request finishes unless it is explicitly persisted.

## Background Workflow

The project includes a background endpoint using FastAPI `BackgroundTasks`.

```http
POST /agent/background/
```

The endpoint immediately returns an accepted response while AI processing continues after the HTTP response has been sent.

Example request:

```json
{
  "message": "Поясни детально різницю між Docker image і container"
}
```

Example immediate response:

```json
{
  "status": "accepted",
  "message": "Поясни детально різницю між Docker image і container"
}
```

The generated result is currently written to application logs.

> `BackgroundTasks` is suitable for this educational project. For durable production job processing, a dedicated queue such as Celery or RQ would normally be preferred.

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

- Default: `10`
- Minimum: `1`
- Maximum: `100`

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

### Agent Query

```http
POST /agent/query/
```

Example request:

```json
{
  "message": "Запам'ятай: клієнта звати Андрій"
}
```

Example response:

```json
{
  "message": "Запам'ятай: клієнта звати Андрій",
  "answer": "Нотатку збережено. ID: 1"
}
```

Another example:

```json
{
  "message": "Як звати клієнта?"
}
```

The agent can select `GET_NOTES`, read memory from PostgreSQL, and generate an answer from the saved notes.

### Background Agent Task

```http
POST /agent/background/
```

Starts AI processing in the background and returns immediately.

### Prometheus Metrics

```http
GET /metrics
```

Exposes application metrics in Prometheus format.

## Ollama

Install Ollama and download/run the model:

```bash
ollama run qwen2.5:3b
```

Check installed models:

```bash
ollama list
```

Ollama normally runs on the host machine at:

```text
http://localhost:11434
```

When FastAPI runs inside Docker, Docker Compose accesses host Ollama through:

```text
http://host.docker.internal:11434
```

## Environment Variables

Create a `.env` file in the project root.

Example for local development:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/fastapi_ai
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

Do **not** commit `.env` to GitHub.

Docker Compose overrides the database and Ollama addresses required inside the FastAPI container.

## Run Locally Without Docker

Make sure PostgreSQL and Ollama are available, then start FastAPI directly:

```bash
uvicorn main:app --reload
```

In this mode FastAPI runs directly on the host Python environment.

## Run With Docker

Make sure:

- Docker Desktop is running
- Ollama is running on the host machine
- `qwen2.5:3b` is installed

Build and start the complete stack:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
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

- Host port: `5433`
- Container port: `5432`

Connect manually:

```bash
docker exec -it fastapi_ai_db psql -U postgres -d fastapi_ai
```

View stored AI requests:

```sql
SELECT * FROM ai_requests ORDER BY id DESC;
```

View agent notes:

```sql
SELECT * FROM notes ORDER BY id DESC;
```

Exit PostgreSQL:

```text
\q
```

## SQLAlchemy

The project uses asynchronous SQLAlchemy.

`database.py` creates:

- `engine` — connection mechanism to PostgreSQL
- `AsyncSessionLocal` — factory for async database sessions
- `get_db()` — provides a database session to FastAPI endpoints

## Alembic Migrations

Alembic manages database schema changes.

Check current migration:

```bash
alembic current
```

Create a migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

The Docker application container automatically runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

## Tests

Run tests locally:

```bash
python -m pytest
```

The current test suite covers core API behavior such as:

- health endpoint
- successful AI endpoint behavior
- request validation
- prompt length validation
- AI service failure handling
- HTTP status codes
- response JSON

External Ollama calls are replaced with fake responses in unit tests using `monkeypatch` where appropriate.

## Validation and Error Handling

Prompt requirements:

- Minimum length: `1` character
- Maximum length: `1000` characters

Invalid input returns:

```text
422 Unprocessable Entity
```

If the AI service is unavailable:

```text
502 Bad Gateway
```

If an AI request exceeds the configured timeout:

```text
504 Gateway Timeout
```

## Docker Services

The Docker Compose stack contains four services:

- `app` — FastAPI application
- `db` — PostgreSQL database
- `prometheus` — metrics collection
- `grafana` — metrics visualization

The FastAPI container waits until PostgreSQL becomes healthy before starting.

## Monitoring

FastAPI exposes Prometheus-compatible metrics at:

```text
http://127.0.0.1:8000/metrics
```

Prometheus UI:

```text
http://127.0.0.1:9090
```

Grafana UI:

```text
http://127.0.0.1:3000
```

Inside Docker Compose, Grafana connects to Prometheus using:

```text
http://prometheus:9090
```

Monitoring flow:

```text
FastAPI
   │
   │ /metrics
   ▼
Prometheus
   │
   │ PromQL
   ▼
Grafana
```

Example PromQL queries:

```promql
http_requests_total
```

```promql
rate(http_requests_total[1m])
```

## CI/CD

GitHub Actions runs automated checks on pushes and pull requests.

CI flow:

```text
Push / Pull Request
  ↓
GitHub Actions runner
  ↓
Start temporary PostgreSQL service
  ↓
Install Python dependencies
  ↓
Run Alembic migrations
  ↓
Run Pytest
```

After tests pass, the pipeline builds a Docker image and pushes it to GitHub Container Registry.

```text
Tests pass
  ↓
Build Docker image
  ↓
Push to GHCR
```

Current image name:

```text
ghcr.io/maaksym/fastapi-ollama-api:latest
```

This is CI plus delivery of a deployable image to a registry. A production server deployment step is not currently included.

## Swagger

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

From Swagger you can test:

```text
GET  /health/
POST /ai/generate/
GET  /ai/history/
POST /agent/query/
POST /agent/background/
GET  /metrics
```

## Security Notes

The `.env` file is ignored by Git and should never be committed.

Recommended `.gitignore` entries:

```gitignore
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
```

Recommended `.dockerignore` entries:

```dockerignore
.venv
__pycache__
*.pyc
.env
.git
.pytest_cache
```

## Quick Verification

From a clean Docker start:

```bash
docker compose down
docker compose up -d --build
docker compose ps
```

Then check:

```text
http://127.0.0.1:8000/health/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/metrics
```

Recommended Swagger checks:

```text
1. POST /ai/generate/       → normal AI response
2. POST /agent/query/       → save a note
3. POST /agent/query/       → read saved memory
4. POST /agent/query/       → ask for weather
5. POST /agent/background/  → verify background processing in logs
```

## What This Project Demonstrates

This project combines traditional backend development with practical AI-agent concepts:

```text
FastAPI API
+ async PostgreSQL
+ Ollama LLM
+ AI tool selection
+ persistent memory
+ multi-step logic
+ background workflow
+ external API integration
+ Docker
+ monitoring
+ tests
+ CI/CD
```

It is intentionally small enough to understand end-to-end while still demonstrating the main building blocks of a modern AI-enabled backend service.
