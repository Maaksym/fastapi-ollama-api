FastAPI AI Project

FastAPI AI application that accepts user prompts, generates responses using a local Ollama model, returns the AI response to the user, and stores prompt/response history in PostgreSQL.

Features

Send prompts to a local AI model through REST API

Generate and return AI responses to users

Local AI inference with Ollama and Qwen2.5 3B

Store prompts and AI responses in PostgreSQL

View AI request history

Limit the number of history records returned

FastAPI REST API

Pydantic validation

Async SQLAlchemy

Alembic migrations

Docker Compose

Docker healthchecks

Prometheus monitoring

Grafana dashboards

Pytest tests

Swagger documentation

Tech Stack

Python 3.14

FastAPI

Uvicorn

Ollama

Qwen2.5 3B

PostgreSQL

SQLAlchemy

asyncpg

Alembic

Docker

Docker Compose

Prometheus

Grafana

prometheus-fastapi-instrumentator

Pytest

HTTPX

Project Structure

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

Architecture

The main request flow is:

User
→ POST /ai/generate/
→ FastAPI Router
→ Service
→ Ollama
→ AI Response
→ Repository saves prompt + answer
→ PostgreSQL
→ FastAPI returns JSON response to User

Main file responsibilities:

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

API Endpoints

Health Check

GET /health/

Example response:

{
  "status": "ok"
}

Generate AI Response

POST /ai/generate/

Example request:

{
  "prompt": "Що таке FastAPI?"
}

Example response:

{
  "prompt": "Що таке FastAPI?",
  "answer": "FastAPI — це сучасний Python-фреймворк для створення API."
}

The generated prompt and answer are stored in PostgreSQL.

AI Request History

GET /ai/history/?limit=5

The limit query parameter controls how many recent records are returned.

Default:

10

Minimum:

1

Maximum:

100

Example response:

[
  {
    "id": 1,
    "prompt": "Що таке FastAPI?",
    "answer": "FastAPI — це сучасний Python-фреймворк для створення API.",
    "created_at": "2026-08-12T11:45:34.868047"
  }
]

Ollama

Install Ollama and download the model:

ollama run qwen2.5:3b

Check installed models:

ollama list

Ollama normally runs locally on:

http://localhost:11434

When FastAPI runs inside Docker, Docker Compose uses:

http://host.docker.internal:11434

to access Ollama running on the host machine.

Environment Variables

Create a .env file in the project root.

Example for local development:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/fastapi_ai
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b

Do not commit .env to GitHub.

Docker Compose overrides the database and Ollama addresses required inside the FastAPI container.

Run With Docker

Make sure:

Docker Desktop is running

Ollama is running

qwen2.5:3b is installed

Build and start the application:

docker compose up -d --build

Check containers:

docker compose ps

Expected result:

fastapi_ai_app   healthy
fastapi_ai_db    healthy

Open Swagger:

http://127.0.0.1:8000/docs

Health endpoint:

http://127.0.0.1:8000/health/

Stop containers:

docker compose down

PostgreSQL

PostgreSQL runs inside Docker.

Host port:

5433

Container port:

5432

Connect manually:

docker exec -it fastapi_ai_db psql -U postgres -d fastapi_ai

View stored AI requests:

SELECT * FROM ai_requests;

Exit PostgreSQL:

\q

SQLAlchemy

The project uses asynchronous SQLAlchemy.

database.py creates:

engine
→ connection mechanism to PostgreSQL

AsyncSessionLocal
→ factory for database sessions

get_db()
→ provides a database session to FastAPI endpoints

Alembic Migrations

Alembic manages database schema changes.

Check the current migration:

alembic current

Create a new migration after changing SQLAlchemy models:

alembic revision --autogenerate -m "migration message"

Apply migrations:

alembic upgrade head

Docker automatically runs:

alembic upgrade head

before starting Uvicorn.

Tests

Run tests:

python -m pytest

Tests currently verify:

health endpoint

successful AI endpoint behavior

empty prompt validation

missing prompt validation

prompt maximum length

AI service failure handling

HTTP status codes

response JSON

External Ollama calls are replaced with fake responses in unit tests using monkeypatch.

Validation

Prompt requirements:

minimum length: 1 character
maximum length: 1000 characters

Invalid input returns:

422 Unprocessable Entity

If the AI service is unavailable:

502 Bad Gateway

If the AI request exceeds the configured timeout:

504 Gateway Timeout

Docker Services

The project uses four Docker services:

app
→ FastAPI application

db
→ PostgreSQL database

The FastAPI container waits until PostgreSQL becomes healthy before starting.

Both services have Docker healthchecks.

Monitoring

The project includes application monitoring with Prometheus and Grafana.

FastAPI exposes Prometheus-compatible metrics at:

http://127.0.0.1:8000/metrics

Prometheus collects these metrics from the FastAPI application and stores time-series data such as request counts, request rates, response status codes, and request duration.

Prometheus UI:

http://127.0.0.1:9090

Grafana uses Prometheus as a data source to visualize application metrics.

Grafana UI:

http://127.0.0.1:3000

Inside Docker Compose, Grafana connects to Prometheus using:

http://prometheus:9090

Monitoring flow:

FastAPI
   │
   │ /metrics
   ▼
Prometheus
   │
   │ PromQL
   ▼
Grafana

Example PromQL queries:

http_requests_total

rate(http_requests_total[1m])

The complete stack can be started with Docker Compose:

docker compose up -d --build

Swagger

FastAPI automatically generates interactive API documentation.

Open:

http://127.0.0.1:8000/docs

From Swagger you can test:

GET /health/

POST /ai/generate/

GET /ai/history/

Security

The .env file is ignored by Git and should never be committed.

The project .gitignore should include:

.venv/
.env
__pycache__/
*.pyc

The .dockerignore should include:

.venv
__pycache__
*.pyc
.env
.git
.pytest_cache

Final Run

To verify the project from a clean Docker start:

docker compose down
docker compose up -d --build
docker compose ps

Then check:

http://127.0.0.1:8000/health/
http://127.0.0.1:8000/docs

Test AI generation and prompt history through Swagger.