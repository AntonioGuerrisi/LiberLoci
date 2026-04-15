# Changelog

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
