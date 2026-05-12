# Notes App

A full-stack notes application built with FastAPI and vanilla JS, used as a learning project for end-to-end production-grade development.

## Stack

- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Database:** SQLite (development), PostgreSQL (production)
- **Auth:** JWT + bcrypt
- **Testing:** pytest
- **Containers:** Docker, docker-compose
- **CI/CD:** GitHub Actions
- **Deploy:** Render.com

## Quick start (development)

```powershell
# From the project root, with np_venv activated:
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- API root: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs

## Project structure

```
notes_app/
├── backend/         FastAPI application
│   ├── app/         Source code
│   ├── tests/       pytest tests
│   ├── requirements.txt
│   └── .env         Local secrets (gitignored)
├── frontend/        HTML/CSS/JS client
└── README.md
```
