# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]
### Added
- Initial project scaffolding, docs, and CI skeleton.
- Flask application factory with `/api/health` endpoint verifying database connectivity.
- `Organization` and `User` SQLAlchemy models with first Alembic migration.
- `Session` model and migration for server-side session storage.
- `/api/auth/signup` — creates a new organization and admin user, with bcrypt password hashing.
- `/api/auth/login` — verifies credentials and issues a server-side session, sent as an httpOnly cookie.
- `login_required` decorator, `/api/auth/me`, and `/api/auth/logout` endpoints.
- Remaining models: `Candidate`, `Application`, `AIAnalysis` (versioned), `RecruiterNote`, `JobDistribution`, `PasswordResetToken`.
- Full Jobs CRUD — create, list (pagination/search/status filter), get, update, delete.
- Full Candidates CRUD with resume upload support (multipart file handling, org-scoped email uniqueness).
- Applications resource linking candidates to jobs with pipeline status tracking (new → screening → interview → offer → hired/rejected).
- `/api/applications/<id>/analyze` — AI-driven candidate/job match analysis via the Anthropic API, with structured JSON prompting and defensive response validation.
- `/api/applications/<id>/analyses` — lists version history of AI analyses for an application.