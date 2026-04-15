# LiberLoci – Copilot Instructions

## Architecture Decisions

- **Monorepo**: `api/` (Python/FastAPI) + `web/` (React/Vite/TypeScript)
- **Database**: PostgreSQL 16, SQLAlchemy 2.0 ORM, Alembic migrations
- **API framework**: FastAPI (sync endpoints, sync SQLAlchemy sessions)
- **Frontend**: React 19 + React Router 7 + TypeScript + Vite 6
- **Cover storage**: bytea in PostgreSQL, processed to JPEG max 900px
- **ISBN lookup**: Google Books → Open Library (fallback chain)
- **Barcode scanning**: html5-qrcode library (browser camera API)
- **Theming**: CSS custom properties with `[data-theme]`, persisted in localStorage
- **Deployment**: Docker Compose (api, web via nginx, db)

## Code Conventions

- All code, comments, UI copy, and docs in **English**.
- Python: formatted with **ruff** (line-length 120).
- TypeScript: **ESLint** with react-hooks and react-refresh plugins.
- Commits: **Conventional Commits** format.
- Tests: focus on ISBN validation/normalization, provider parsing, dedupe logic.

## Key Files

| Purpose               | Path                                      |
| --------------------- | ----------------------------------------- |
| API entry point       | `api/app/main.py`                         |
| DB models             | `api/app/models.py`                       |
| API schemas           | `api/app/schemas.py`                      |
| ISBN utilities        | `api/app/utils/isbn.py`                   |
| ISBN lookup service   | `api/app/services/isbn_lookup.py`         |
| Cover processing      | `api/app/services/cover.py`               |
| Search logic          | `api/app/services/search.py`              |
| DB migration          | `api/alembic/versions/0001_*.py`          |
| Seed data             | `api/seed.py`                             |
| Frontend entry        | `web/src/main.tsx`                        |
| React routes          | `web/src/App.tsx`                         |
| API client            | `web/src/api/client.ts`                   |
| Docker Compose        | `docker-compose.yml`                      |

## Data Model Summary

- **Book**: title, authors, isbn13 (partial unique), isbn10, publisher, publishedYear, language, format, readingStatus, tags (text[]), locationId, notes, providerRawJson (jsonb)
- **Location**: room, shelf, level, sortOrder
- **Cover**: bookId (PK+FK), data (bytea), mimeType, checksum, width, height

## API Endpoints

- `GET /api/books?query=` – search books
- `GET /api/books/by-isbn/{isbn}` – find by ISBN
- `POST /api/books` – create book (with dedupe)
- `GET /api/books/{id}` – get book
- `PATCH /api/books/{id}` – update book
- `DELETE /api/books/{id}` – delete book
- `GET /api/books/{id}/cover` – get cover image
- `PUT /api/books/{id}/cover` – upload cover
- `POST /api/isbn/lookup` – ISBN metadata lookup
- `GET /api/locations` – list locations
- `POST /api/locations` – create location
- `GET /api/tags` – list all tags
- `GET /api/library/export` – full JSON export
- `POST /api/library/import` – full JSON import
