# NoteStack

A small, production-grade full-stack notes application built as an end-to-end learning project. Users register, log in, and manage their own private notes with tags, search, and filters. Everything is wired up the way a real product team would do it — typed schemas, JWT auth, automated tests, containers, CI/CD, structured logs.

**🌐 Live demo:** <https://notestack-k3xg.onrender.com>
**📖 Interactive API docs:** <https://notestack-k3xg.onrender.com/docs>
**❤️ Health probe:** <https://notestack-k3xg.onrender.com/health>

> First request after ~15 minutes of inactivity takes 30–60s — that's Render's free tier waking the container.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Screenshots / what it looks like](#what-it-looks-like)
- [Project structure](#project-structure)
- [Local development](#local-development)
- [Running with Docker + Postgres](#running-with-docker--postgres)
- [Running tests](#running-tests)
- [Environment variables](#environment-variables)
- [API reference](#api-reference)
- [Architecture notes](#architecture-notes)
- [Continuous integration](#continuous-integration)
- [Production deployment (Render)](#production-deployment-render)
- [Development workflow](#development-workflow)
- [Roadmap / next steps](#roadmap--next-steps)

---

## Features

- Email + password registration with **bcrypt-hashed** credentials (no plaintext anywhere)
- **JWT** (HS256) access tokens for session auth
- Full CRUD for notes (title, content, tags) with **per-user data isolation**
- **Many-to-many** tags (a note can have multiple tags; a tag can be on multiple notes)
- Case-insensitive search by query (`?q=`) and filter by tag (`?tag=`)
- **Pagination** (`skip`, `limit` capped at 100)
- Auto-generated, interactive **OpenAPI docs** at `/docs` and `/redoc`
- **Structured logs** with a request ID stamped onto every log line for traceability
- **Global exception handler** — internal errors logged with traceback, generic 500 returned to clients (no info leak)
- **Single origin** deployment — same FastAPI process serves both API and frontend, so no CORS configuration needed
- **22 automated tests** covering happy paths, validation errors, and multi-user ownership boundaries

---

## Tech stack

| Layer | Tools | Why |
|---|---|---|
| **API** | FastAPI 0.115, Pydantic 2 | Type-safe, fast, auto-generated docs |
| **ORM** | SQLAlchemy 2 | Modern `Mapped[...]` typed style |
| **Database** | SQLite (dev) / PostgreSQL 16 (prod) | Same code, different storage — swapped via `DATABASE_URL` |
| **Auth** | PyJWT + bcrypt | Industry-standard token + password hashing |
| **Frontend** | HTML, CSS, vanilla JS — no framework | Demonstrates the web platform; no build step, no bundler |
| **Tests** | pytest + httpx TestClient | 22 tests; in-memory SQLite per test for isolation |
| **Containers** | Docker + docker-compose | One-command Postgres-backed local stack |
| **CI** | GitHub Actions | Tests run on every push and PR |
| **Hosting** | Render.com (free tier) | Managed Docker + Postgres, IaC via `render.yaml` |

---

## What it looks like

The app is two simple pages:

1. **`/login.html`** — Sign in / Create account, with tabs and inline error messages
2. **`/`** — Notes dashboard:
   - Top bar with the logged-in user's email and a Sign out button
   - "New note" form (title, content, comma-separated tags)
   - Search box (debounced 300ms) and tag filter dropdown
   - Notes as cards with Edit and Delete buttons

Both pages styled with a single `styles.css` using CSS variables, system font stack, and ~150 lines of CSS.

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
│   │   ├── main.py                FastAPI entry: middleware, lifespan, static mount
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
│   │   ├── test_auth.py           8 tests
│   │   ├── test_notes.py          11 tests
│   │   └── test_tags.py           3 tests
│   ├── .env                       Local secrets (gitignored)
│   ├── .env.example               Template, committed
│   ├── Dockerfile                 Production image
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

## Local development

### Prerequisites

- **Python 3.12+**
- **Git**
- **Docker Desktop** (only required for the Postgres-backed run below)

### 1. Clone and create a virtual environment

```powershell
git clone https://github.com/<your-username>/notes-app.git
cd notes-app
python -m venv np_venv
np_venv\Scripts\activate
```

### 2. Install dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Generate your SECRET_KEY and create `.env`

```powershell
# Generate a key (do this ONCE)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the template
copy .env.example .env
```

Open `backend/.env` and replace the placeholder `SECRET_KEY` value with the string you just generated.

### 4. Run the dev server

```powershell
uvicorn app.main:app --reload
```

Open **<http://127.0.0.1:8000>** in your browser. You'll see the login page; register an account and start creating notes. The SQLite database file is at `backend/notes.db`.

---

## Running with Docker + Postgres

For a production-shaped local environment (Postgres instead of SQLite), run the docker-compose stack from the **project root**:

```powershell
docker compose up --build
```

Two containers come up:

| Service | What it is |
|---|---|
| `db` | Postgres 16 (alpine), data persisted in a named volume `postgres_data` |
| `backend` | The FastAPI app, built from `backend/Dockerfile`, talking to `db` via the compose network |

Same URL: **<http://localhost:8000>**. The web service reads its env from `backend/.env` plus the compose-level overrides (`ENVIRONMENT=production`, `DATABASE_URL=postgresql+psycopg2://...`).

```powershell
# Stop containers (keeps the Postgres data in the volume)
docker compose down

# Stop and DELETE the Postgres data
docker compose down -v

# Inspect the Postgres data directly
docker compose exec db psql -U notes -d notes -c "SELECT id, email FROM users;"
```

---

## Running tests

```powershell
cd backend
pytest
```

Expected: **22 passed in under 10 seconds**. Tests use an **in-memory SQLite** database that is created fresh per test, so they never touch your real `notes.db` or your Postgres instance.

Useful flags:

```powershell
pytest -v                                              # verbose
pytest -k "ownership or auth"                          # only matching tests
pytest tests/test_auth.py::test_login_returns_token    # single test
pytest -x                                              # stop at first failure
pytest -s                                              # show print() / logging output
```

---

## Environment variables

All configuration comes from environment variables (or `backend/.env` for local dev). Defined in [`backend/app/config.py`](backend/app/config.py).

| Variable | Required | Default | Used for |
|---|---|---|---|
| `APP_NAME` | No | `NoteStack` | OpenAPI title |
| `ENVIRONMENT` | No | `development` | `development` → human logs; anything else → JSON logs |
| `DEBUG` | No | `true` | Reserved (not currently used by app logic) |
| `DATABASE_URL` | No | `sqlite:///./notes.db` | Any SQLAlchemy URL — SQLite or `postgresql://...` |
| `SECRET_KEY` | **Yes** | _(none — app refuses to start)_ | Signs JWTs. Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token lifetime |

A starter template lives at [`backend/.env.example`](backend/.env.example).

---

## API reference

Interactive docs at **`/docs`** (Swagger UI) and **`/redoc`** (ReDoc) — both auto-generated from FastAPI route definitions and Pydantic schemas.

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
| `GET` | `/tags` | Yes | List own tags, alphabetical |
| `GET` | `/health` | No | Health probe — `{status: ok}` |

Auth uses the standard `Authorization: Bearer <token>` header. Tokens are JWTs signed with `SECRET_KEY` and carry the user's email in the `sub` claim. The [`get_current_user`](backend/app/core/deps.py) dependency decodes the token and loads the user.

**Ownership is enforced on every notes/tags query**: `WHERE user_id = current_user.id` is appended to every read/write. Requests for someone else's note return 404 (not 403) so we don't reveal whether the ID exists.

### Quick curl example

```bash
# Register
curl -X POST https://notestack-k3xg.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# Login (note: form data, not JSON)
TOKEN=$(curl -X POST https://notestack-k3xg.onrender.com/auth/login \
  -d "username=you@example.com&password=yourpassword" | jq -r .access_token)

# Create a note
curl -X POST https://notestack-k3xg.onrender.com/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first note","content":"hello","tag_names":["work"]}'

# List notes
curl https://notestack-k3xg.onrender.com/notes -H "Authorization: Bearer $TOKEN"
```

---

## Architecture notes

### Two-model separation (DB vs API)

DB models in [`backend/app/models/`](backend/app/models/) describe what's stored. Pydantic schemas in [`backend/app/schemas/`](backend/app/schemas/) describe what crosses the HTTP boundary. They're deliberately separate: `User` (DB) has `hashed_password`; `UserRead` (API) does not, so password hashes can never leak. Same idea for server-managed fields like `id` and `created_at` — they're output-only.

### Dependency injection for `db` and `current_user`

Endpoints declare `db: Session = Depends(get_db)` and `current_user: User = Depends(get_current_user)`. FastAPI injects them. This makes tests trivial — `app.dependency_overrides[get_db] = override_get_db` swaps the real DB for an in-memory test DB without changing a line of route code.

### Request-id correlation

[`RequestLoggingMiddleware`](backend/app/middleware.py) generates a UUID per request, stores it in a `ContextVar`, returns it in the `X-Request-ID` response header, and logs an access line. The logging filter ([`backend/app/utils/logging.py`](backend/app/utils/logging.py)) reads the ContextVar on every log record, so any `logger.info(...)` deep inside a route is automatically stamped with the same `request_id`. **To trace an issue, grep your logs for one request ID.**

### Log format auto-switches by environment

In `ENVIRONMENT=development` you get compact human lines (`12:34:56 INFO [a1b2c3d4] app: ...`). Anything else flips to one JSON object per line — exactly what Render's log viewer (and Datadog, etc.) want.

### Storage portability

`DATABASE_URL` is the **only** thing that changes between local SQLite, Docker Postgres, and Render Postgres. App code is identical. The compose file passes `postgresql+psycopg2://...`; Render injects `postgresql://...` via `render.yaml`'s `fromDatabase`. SQLAlchemy handles both.

> Schema creation currently uses `Base.metadata.create_all()` at startup. Fine for new tables but cannot handle schema changes on existing tables. **Adopt Alembic the moment you need to alter a column.**

### Security choices

- **bcrypt** with random salt per password ([`backend/app/core/security.py`](backend/app/core/security.py))
- **JWT** in `localStorage` on the client. Trade-off: simpler than cookies, but vulnerable to XSS if you have any — which is why every place we put user data into the DOM goes through an `escapeHtml` helper ([`frontend/js/app.js`](frontend/js/app.js))
- **404 instead of 403** on someone else's resources — leaks zero info about IDs
- Global exception handler returns a generic 500 to clients while logging the full traceback server-side — no stack traces leak to the public

---

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request targeting `main`:

1. Check out the code
2. Set up Python 3.12 with pip cache (`cache: pip`)
3. Install `backend/requirements.txt`
4. Run `pytest`

A failing CI run shows up as a red ✗ on the commit and emails you. CI completes in ~30 seconds (with the cache warm).

---

## Production deployment (Render)

[`render.yaml`](render.yaml) describes the entire production environment as code:

- A web service running the backend Docker image, with health-checked deploys
- A managed PostgreSQL 16 instance, with daily backups
- `SECRET_KEY` generated at provision time by Render (never seen by anyone)
- `DATABASE_URL` injected from the managed database — no hardcoded credentials

### First-time deploy

1. Sign up at <https://render.com> using GitHub
2. Render dashboard → **New +** → **Blueprint**
3. Select this repo → **Apply**
4. Wait ~5 min for the first build and DB provisioning
5. Open the URL Render shows on the service page

### Subsequent deploys

Just push to `main`. Render watches the branch, rebuilds the Docker image, and rolls the deploy live in ~3 minutes — zero clicks.

### Logs

Render's service dashboard → **Logs** tab streams the same JSON output the app produces in production mode. Filter by `request_id`, `level`, `path`, etc.

### Free-tier caveats

- Web service spins down after 15 min idle; the next request takes 30–60s to wake the container.
- Free PostgreSQL has a time-limited grace period — Render emails you before expiry; upgrade or migrate data before then.
- Both are fine for a learning/demo project; upgrade to paid tiers when you have real users.

---

## Development workflow

```powershell
# Make changes locally
# Run tests
cd backend
pytest

# Commit + push
cd ..
git add .
git commit -m "Describe what you changed"
git push

# GitHub Actions runs your tests automatically (~30s)
# Render auto-deploys to production if the push was to main (~3 min)
```

To check the production logs after a deploy:

1. https://dashboard.render.com → your service
2. **Logs** tab → tail the JSON lines as they come in
3. To find a specific request a user reported: grep the logs for the `X-Request-ID` from their browser DevTools

---

## Roadmap / next steps

If you want to extend this project, sensible follow-ups in roughly increasing difficulty:

- **Dark mode** toggle (a CSS class on `<body>`, a button in the header, persist choice in `localStorage`)
- **Edit-in-place** for notes (current "Edit" mutates the create form — replace with inline editing on the card)
- **Markdown rendering** in note content
- **Pin / archive** notes (boolean flag on the model, filter in `list_notes`)
- **Note sharing by link** (create a public read-only token tied to a note)
- **Adopt Alembic** for migrations — needed as soon as you change a column
- **Rate limiting** on `/auth/register` and `/auth/login` (e.g., `slowapi` + a Redis service)
- **HTML email** for password reset (Render env var for an SMTP URL, or use a service like Postmark)
- **Custom domain** on Render (one DNS record + a button in the dashboard)
- **httpOnly cookie auth** to harden against XSS (more secure than `localStorage` for the JWT)

---

## License

MIT — free to use this as a starting point for your own projects.
