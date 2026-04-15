# LiberLoci

**Self-hosted book inventory** — know what you own, find it fast.

LiberLoci is a responsive web app to catalogue your personal book collection. It works great on desktop for detailed management and on mobile for quick "do I already own this?" lookups while browsing a bookstore.

## Features (V1)

- **ISBN barcode scanning** via phone camera — instant owned/not-owned feedback with location
- **Search** by title, author, or ISBN (case-insensitive, contains matching)
- **Manual add/edit** when metadata is missing
- **ISBN lookup** via Google Books and Open Library (with automatic fallback)
- **Location tree** — Room → Shelf → Level → browse your books physically
- **Cover management** — auto-download from providers, resize to JPEG (max 900px)
- **Tags** and **reading status** tracking
- **Light + Dark theme** with system preference detection
- **Full JSON export/import** (including cover bytes) for portability
- **Deduplication** — ISBN-13 unique constraint + soft title/author matching

## Tech Stack

| Layer     | Tech                                          |
|-----------|-----------------------------------------------|
| API       | Python 3.12, FastAPI, SQLAlchemy 2, Alembic   |
| Frontend  | React 19, TypeScript, Vite 6, React Router 7  |
| Database  | PostgreSQL 16                                  |
| Scanner   | html5-qrcode (browser camera)                 |
| Deploy    | Docker Compose                                 |

## Quick Start (Docker)

```bash
# Clone the repo
git clone https://github.com/AntonioGuerrisi/LiberLoci.git
cd LiberLoci

# Start everything
docker compose up --build

# Seed demo data (optional)
docker compose exec api python seed.py
```

Open **http://localhost:3000** in your browser.

- Web UI: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

## Local Development

### 1. Start a local PostgreSQL database

The easiest way is to start **only** the `db` service from Docker Compose:

```bash
docker compose up -d db
```

This starts PostgreSQL 16 on `localhost:5432` (user: `liberloci`, password: `liberloci`, database: `liberloci`). Verify it is ready:

```bash
docker compose exec db pg_isready -U liberloci
```

### 2. API

**Windows (PowerShell):**

```powershell
cd api

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Point to the local database
$env:DATABASE_URL="postgresql://liberloci:liberloci@localhost:5432/liberloci"

# Run migrations
alembic upgrade head

# Seed demo data
python seed.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

**macOS / Linux (bash):**

```bash
cd api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Point to the local database
export DATABASE_URL=postgresql://liberloci:liberloci@localhost:5432/liberloci

# Run migrations
alembic upgrade head

# Seed demo data
python seed.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### 3. Web

```bash
cd web
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

### Running Tests

```bash
cd api
pip install -r requirements.txt
pytest
```

### Linting

```bash
# Python
cd api
ruff check .
ruff format .

# TypeScript
cd web
npm run lint
```

## Database Backup & Restore

```bash
# Backup
docker compose exec db pg_dump -U liberloci liberloci > backup.sql

# Restore
docker compose exec -T db psql -U liberloci liberloci < backup.sql
```

## Export / Import

```bash
# Export full library (JSON with base64 covers)
curl http://localhost:3000/api/library/export > library.json

# Import
curl -X POST http://localhost:3000/api/library/import \
  -F "file=@library.json"
```

## API Endpoints

| Method | Endpoint                    | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | `/api/books?query=`         | Search books                 |
| GET    | `/api/books/by-isbn/{isbn}` | Find book by ISBN            |
| POST   | `/api/books`                | Create book (with dedupe)    |
| GET    | `/api/books/{id}`           | Get book details             |
| PATCH  | `/api/books/{id}`           | Update book                  |
| DELETE | `/api/books/{id}`           | Delete book                  |
| GET    | `/api/books/{id}/cover`     | Get cover image              |
| PUT    | `/api/books/{id}/cover`     | Upload cover                 |
| POST   | `/api/isbn/lookup`          | ISBN metadata lookup         |
| GET    | `/api/locations`            | List locations               |
| POST   | `/api/locations`            | Create location              |
| GET    | `/api/tags`                 | List all tags                |
| GET    | `/api/library/export`       | Full library export (JSON)   |
| POST   | `/api/library/import`       | Full library import (JSON)   |

## Project Structure

```
LiberLoci/
├── api/                    # Python/FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app & routes
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic
│   │   └── utils/          # ISBN validation, etc.
│   ├── alembic/            # DB migrations
│   ├── tests/              # Pytest tests
│   └── seed.py             # Demo data seeder
├── web/                    # React/TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route pages
│   │   ├── api/            # API client
│   │   ├── hooks/          # React hooks
│   │   └── types/          # TypeScript types
│   └── nginx.conf          # Production nginx config
├── docker-compose.yml
├── SMOKE_TESTS.md          # Manual test checklist
└── copilot-instructions.md # AI coding assistant context
```

## License

This software is distributed under the **GNU General Public License v3.0** — see [LICENSE](LICENSE) for details.

**Trademark Notice:** The project name "LiberLoci" and associated logos are protected by trademark. The GPLv3 license grants rights to the source code but does **not** grant rights to use the trademarked name or logos in ways that imply endorsement. Derivative distributions must comply with GPLv3; use of the trademarked name/logos may require permission.
