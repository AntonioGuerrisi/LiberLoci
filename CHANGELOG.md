# Changelog

## [0.4.2+10] - 2026-09-01
### Fixed
- Fix homepage location filtering so shelf view shows books correctly and is no longer limited by the backend search result size.

## [0.4.1+9] - 2026-05-04
### Improved
- ISBN input field is automatically focused when opening the Add Book page

## [0.4.0+8] - 2026-04-28
### Improved
- ISBN lookup field triggers lookup on Enter key press

## [0.4.0+7] - 2026-04-28
### Added
- WorldCat xISBN provider for ISBN metadata lookup (free, no API key, good Italian book coverage)
- BNF (Bibliothèque nationale de France) provider via SRU/Dublin Core XML (free, good European coverage)
- Fallback chain updated: Google Books → WorldCat → BNF → Open Library
### Fixed
- Google Books API key (`GOOGLE_BOOKS_API_KEY`) was configured but never passed to API calls; now included in requests when set, increasing the daily quota significantly

## [0.3.0+6] - 2026-04-16
### Added
- Settings page with location management (create, edit, delete)
- Gear icon in header navigation for Settings access
- Server-side cover download proxy endpoint (`POST /api/books/{id}/cover-from-url`)
- `updateLocation` and `deleteLocation` API client functions
### Fixed
- Google Books covers not downloading due to browser CORS restrictions (now downloaded server-side)
- Location delete now safely unlinks books before removing
- TypeScript build errors (unused imports, incorrect type annotations) the location

## [0.2.0+4] - 2026-04-15
### Added
- HTTPS support with auto-generated self-signed certificate for camera access from remote devices
- Port 3443 exposed for HTTPS in Docker Compose
- Persistent volume for TLS certificates (survives container rebuilds)
### Improved
- Scanner error message now explains HTTPS requirement when camera fails on non-localhost
- HTTP requests automatically redirect to HTTPS

## [0.1.1+3] - 2026-04-15
### Fixed
- Docker web build failing because `tsc` not found (`npm ci --include=dev` in Dockerfile)
