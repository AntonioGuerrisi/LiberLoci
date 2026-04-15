# Smoke Test Checklist

Verify these scenarios after each deployment or significant change.

## Setup

- [ ] `docker compose up --build` starts all services without errors
- [ ] API responds at `http://localhost:8000/api/health` with `{"status":"ok"}`
- [ ] Web UI loads at `http://localhost:3000`

## Seed Data

- [ ] Run `docker compose exec api python seed.py` – creates demo books and locations
- [ ] Home page shows seeded books

## Search

- [ ] Search by title (e.g., "Dune") returns matching books
- [ ] Search by author (e.g., "Orwell") returns matching books
- [ ] Search by ISBN (e.g., "9780451524935") returns exact match first
- [ ] Search is case-insensitive
- [ ] Empty search returns all books

## ISBN Scan (Mobile)

- [ ] `/scan` page opens camera (requires HTTPS or localhost)
- [ ] Scanning a known ISBN shows "Owned" with location and notes
- [ ] Scanning an unknown ISBN shows "Not owned" with "Add" CTA
- [ ] "Add This Book" navigates to add form with ISBN pre-filled

## ISBN Lookup

- [ ] `POST /api/isbn/lookup` with valid ISBN returns metadata
- [ ] Invalid ISBN returns 400 with clear message
- [ ] ISBN not found returns 404 with manual-add suggestion

## Add / Edit Book

- [ ] Manual add with title + authors creates a book
- [ ] ISBN lookup pre-fills the form
- [ ] Duplicate ISBN returns existing book instead of creating new
- [ ] Edit updates book metadata correctly
- [ ] Cover upload resizes and converts to JPEG

## Locations

- [ ] Location tree shows rooms → shelves → levels
- [ ] Filtering by location works on home page
- [ ] Adding a new location via API works

## Theme

- [ ] Light/Dark toggle switches theme
- [ ] Theme persists across page reloads
- [ ] Defaults to system preference when unset

## Export / Import

- [ ] `GET /api/library/export` returns JSON with books, locations, covers (base64)
- [ ] Import from exported JSON recreates library (POST with file upload)
- [ ] Duplicate books are skipped during import

## Deduplication

- [ ] Adding a book with existing ISBN-13 returns the existing book
- [ ] Adding a book without ISBN but matching title+authors returns existing book
