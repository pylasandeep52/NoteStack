# Notes App

A small, production-grade full-stack notes application built as an end-to-end learning project. Users register, log in, and manage their own private notes with tags, search, and filters. Everything is wired up the way a real product team would do it — typed schemas, JWT auth, automated tests, containers, CI/CD, structured logs.

**Live demo:** _add your Render URL here after Phase 10B_
**API docs (Swagger UI):** `https://<your-url>/docs`

---

## Features

- Email + password registration with **bcrypt-hashed** credentials
- **JWT** (HS256) access tokens for session auth
- Full CRUD for notes (title, content, tags) with **per-user data isolation**
- **Many-to-many** tags (a note can have multiple tags; a tag can be on multiple notes)
- Full-text-ish search by query (`?q=`) and filter by tag (`?tag=`)
- **Pagination** (`skip`, `limit` capped at 100)
- Auto-generated, interactive **OpenAPI docs** at `/docs` and `/redoc`
- **Structured logs** with a request ID stamped onto every log line for traceability
- **Global exception handler** — internal errors logged with traceback, generic 500 returned to clients (no information leak)

---

## Tech stack

| Layer | Tools | Why |
|---|---|---|
| **API** | FastAPI 0.115, Pydantic 2 | Type-safe, fast, auto-generated docs |
| **ORM** | SQLAlchemy 2 | Modern `Mapped[...]` typed style |
| **Database** | SQLite (dev) / PostgreSQL 16 (prod) | Same code, different storage — swapped via `DATABASE_URL` |
| **Auth** | PyJWT + bcrypt | Industry-standard token + password hashing |
| **Frontend** | HTML, CSS, vanilla JS — no framework | Demonstrates the platform; no build step |
| **Tests** | pytest + httpx TestClient | 22 tests covering API, auth, ownership boundaries |
| **Containers** | Docker + docker-compose | One-command Postgres-backed local stack |
| **CI** | GitHub Actions | Tests run on every push and PR |
| **Hosting** | Render.com (free tier) | Managed Docker + Postgres, IaC via `render.yaml` |

---

## Project structure

```
notes_app/
├── .github/
│   └── workflows/
│       └── ci.yml                 GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                FastAPI entry point, middleware, lifespan, static mount
│   │   ├── config.py              Settings loaded from .env via pydantic-settings
│   │   ├── database.py            SQLAlchemy engine, SessionLocal, Base, get_db dependency
│   │   ├── middleware.py          RequestLoggingMiddleware (request ID + duration)
│   │   ├── models/                SQLAlchemy ORM models
│   │   │   ├── user.py            User
│   │   │   ├── note.py            Note
│   │   │   └── tag.py             Tag + note_tags association table
│   │   ├── schemas/               Pydantic request/response schemas
│   │   │   ├── user.py            UserCreate, UserLogin, UserRead
│   │   │   ├── note.py            NoteCreate, NoteUpdate, NoteRead
│   │   │   ├── tag.py             TagRead
│   │   │   └── token.py           Token, TokenData
│   │   ├── core/
│   │   │   ├── security.py        hash_password, verify_password, JWT encode/decode
│   │   │   └── deps.py            get_current_user FastAPI dependency
│   │   ├── routers/
│   │   │   ├── auth.py            /auth/register, /auth/login, /auth/me
│   │   │   ├── notes.py           Notes CRUD (POST/GET/PATCH/DELETE)
│   │   │   └── tags.py            GET /tags
│   │   └── utils/
│   │       └── logging.py         RequestIdFilter, JsonFormatter, HumanFormatter
│   ├── tests/
│   │   ├── conftest.py            db_session, client, auth_client fixtures
│   │   ├── test_auth.py
│   │   ├── test_notes.py
│   │   └── test_tags.py
│   ├── .env                       Local secrets (gitignored)
│   ├── .env.example               Template, committed
│   ├── Dockerfile                 Image for production / local-with-Postgres
│   ├── pytest.ini                 Test config (pythonpath, testpaths)
│   └── requirements.txt           Pinned Python deps
├── frontend/
│   ├── index.html                 Notes page (requires auth)
│   ├── login.html                 Sign-in / sign-up page
│   ├── css/styles.css
│   └── js/
│       ├── api.js                 Fetch wrapper + api.* methods
│       ├── auth.js                Login page logic
│       └── app.js                 Notes page logic
├── docker-compose.yml             Two-service local stack (backend + Postgres)
├── render.yaml                    Render Blueprint (web service + managed Postgres)
├── .dockerignore
├── .gitignore
└── README.md                      You are here
```

---

## Quick start

### Prerequisites

- **Python 3.12+**
- **Docker Desktop** (only required for the Postgres-backed run, Phase 9 onward)
- A modern browser

### 1. Run locally with SQLite (fastest path)

```powershell
# Create and activate a virtual environment
python -m venv np_venv
np_venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Generate a SECRET_KEY (do this ONCE)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the template and paste the key
copy .env.example .env
# Then edit .env and paste your SECRET_KEY value

# Run the server
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> — registration page. Sign up, create notes. Data lives in `backend/notes.db` (SQLite file).

### 2. Run with Docker + Postgres (production-like)

From the project root (not `backend/`):

```powershell
docker compose up --build
```

Two containers come up: `notes_app-db-1` (Postgres 16) and `notes_app-backend-1` (the FastAPI app). Same URL, <http://localhost:8000>, but now backed by Postgres. Data lives in the `postgres_data` Docker volume and survives container restarts.

```powershell
# Stop containers (keeps the Postgres data)
docker compose down

# Stop AND wipe Postgres data
docker compose down -v

# Inspect the Postgres data directly
docker compose exec db psql -U notes -d notes -c "SELECT id, email FROM users;"
```

### 3. Run the test suite

```powershell
cd backend
pytest
```

Should print **22 passed** in well under 10 seconds. Tests use an in-memory SQLite database per test — no contact with the real `notes.db` or with Postgres.

Useful flags:

```powershell
pytest -v                                              # verbose
pytest -k "notes"                                      # only tests matching substring
pytest tests/test_auth.py::test_login_returns_token    # single test
pytest -x                                              # stop at first failure
```

---

## Environment variables

All settings come from environment variables (or a `.env` file at `backend/.env` for local dev). Pinned in [`backend/app/config.py`](backend/app/config.py).

| Variable | Required | Default | Used for |
|---|---|---|---|
| `APP_NAME` | No | `Notes API` | OpenAPI title |
| `ENVIRONMENT` | No | `development` | `development` enables human-readable logs; anything else uses JSON |
| `DEBUG` | No | `true` | Reserved (currently unused by app logic) |
| `DATABASE_URL` | No | `sqlite:///./notes.db` | Any SQLAlchemy URL: SQLite or `postgresql://...` |
| `SECRET_KEY` | **Yes** | _(none — app refuses to start)_ | Signs JWTs. Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token lifetime |

A starter template lives at [`backend/.env.example`](backend/.env.example).

---

## API reference

Interactive docs at `/docs` (Swagger UI) and `/redoc` (ReDoc) — both auto-generated from the FastAPI route definitions and Pydantic schemas.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create account. Body: `{email, password}`. 201 returns UserRead |
| `POST` | `/auth/login` | No | OAuth2 password flow (form data: `username`, `password`). Returns `{access_token, token_type}` |
| `GET` | `/auth/me` | Yes | Returns the current user |
| `POST` | `/notes` | Yes | Create a note. Body: `{title, content, tag_names}` |
| `GET` | `/notes` | Yes | List own notes. Query: `q`, `tag`, `skip`, `limit` (max 100) |
| `GET` | `/notes/{id}` | Yes | Read one note (404 if not yours) |
| `PATCH` | `/notes/{id}` | Yes | Partial update (any subset of `title`, `content`, `tag_names`) |
| `DELETE` | `/notes/{id}` | Yes | Delete (204 on success, 404 if not yours) |
| `GET` | `/tags` | Yes | List own tags alphabetically |
| `GET` | `/health` | No | Health probe — `{status: ok}` |

Auth uses the standard `Authorization: Bearer <token>` header. Tokens are JWTs signed with `SECRET_KEY` and carry the user's email in the `sub` claim. The `get_current_user` dependency ([`backend/app/core/deps.py`](backend/app/core/deps.py)) decodes the token and loads the User. **Every notes/tags endpoint enforces ownership** by filtering on `Note.user_id == current_user.id`; reads of someone else's note return 404, not 403, so the response doesn't reveal whether the id exists.

---

## Architecture notes

### Two-model separation

DB models ([`backend/app/models/`](backend/app/models/)) describe what's stored. Pydantic schemas ([`backend/app/schemas/`](backend/app/schemas/)) describe what crosses the HTTP boundary. They're deliberately different — `User` (DB) has `hashed_password`; `UserRead` (API) does not, so passwords can never leak in responses. Same idea for fields that are server-managed (`id`, `created_at`) — they're outputs only, never inputs.

### Dependency injection for `db` and `current_user`

The `get_db` and `get_current_user` functions in [`backend/app/database.py`](backend/app/database.py) and [`backend/app/core/deps.py`](backend/app/core/deps.py) are FastAPI dependencies. Every endpoint declares them as parameters (`db: Session = Depends(get_db)`), and FastAPI injects them automatically. This makes tests trivial — `app.dependency_overrides[get_db] = ...` swaps the real DB for an in-memory test DB without changing a line of route code.

### Request-id correlation

[`RequestLoggingMiddleware`](backend/app/middleware.py) generates a UUID for every request, stores it in a `ContextVar`, returns it in the `X-Request-ID` header, and logs the access line. The logging filter in [`backend/app/utils/logging.py`](backend/app/utils/logging.py) reads the ContextVar on every log record, so any `logger.info(...)` deep inside a route handler is automatically stamped with the same request_id. To trace an issue end-to-end, grep your logs for one request ID.

### Log format flips automatically

In `development`, you get compact human lines (`12:34:56 INFO [a1b2c3d4] app: ...`). In any other environment (`production`, `staging`, etc.) you get one JSON object per line, ready for ingestion by log aggregators (Render's log viewer, Datadog, etc.).

### Storage portability

`DATABASE_URL` is the only thing that changes between local SQLite, Docker Postgres, and production Render Postgres. The app code is identical. The compose file sets it explicitly to a `postgresql+psycopg2://...` URL; Render injects a `postgresql://...` URL via `render.yaml`'s `fromDatabase`. SQLAlchemy handles both.

> Note: schema creation currently uses `Base.metadata.create_all()` at startup. That's fine for new tables but cannot handle schema changes on existing tables — add Alembic migrations if you start altering columns.

---

## Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request targeting `main`:

1. Check out the code
2. Set up Python 3.12 with pip cache
3. Install `backend/requirements.txt`
4. Run `pytest`

A failing CI run blocks nothing automatically — but it shows up as a red ✗ on the commit, an email notification, and (if branch protection is enabled) prevents the PR from merging. Tests run in ~30 seconds. The cache makes subsequent runs faster.

---

## Production deployment (Render)

[`render.yaml`](render.yaml) describes the entire production environment:

- Web service running the backend Docker image
- Managed PostgreSQL 16 instance with backups
- `SECRET_KEY` generated at provision time (never seen by anyone, including the developer)
- `DATABASE_URL` injected from the managed database — no hardcoding

Deploying for the first time:

1. Sign up at <https://render.com> using GitHub
2. Render dashboard → **New +** → **Blueprint**
3. Select this repo → **Apply**
4. Wait ~5 min for the first build and DB provisioning
5. Open the URL Render shows in the service page

Every subsequent push to `main` triggers an automatic rebuild and rolling deploy. Logs are visible in the Render dashboard (the same JSON lines this app emits in production mode).

### Free-tier caveats

- Web service spins down after 15 min idle; the next request takes ~30-60s to wake the container
- Free PostgreSQL has a time-limited grace period — Render emails you before expiry; upgrade or migrate data before then
- These are fine for a learning/demo project; upgrade to a paid plan when you have real users

---

## Development workflow

```powershell
# Make changes locally
# Run tests
pytest

# Commit + push
git add .
git commit -m "Describe what you changed"
git push

# GitHub Actions runs your tests automatically (~30s)
# Render auto-deploys if CI passes and the push was to main (~3 min)
```

---

## License

MIT — feel free to use this as a starting point for your own projects.
