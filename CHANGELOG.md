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