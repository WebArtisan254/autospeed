# ProAutoType 🚗⚡

AutoSpeed is a full-stack Flask web application for creating, managing, and publishing entries. Built using the application factory pattern with a clean blueprint architecture, it features user authentication, role-based access control, a RESTful API, an admin dashboard, and background job processing.

**Live:** [proautotype.com](https://proautotype.com)

## About

ProAutoType is my build-and-break-things project. I'd had my eye on Flask for a while, and it wasn't until last fall — when I watched a Flask application get configured with Jenkins for CI/CD pipelines — that I decided to go deeper into it. Flask is great for prototyping and experimenting with APIs, and I wanted to put production and security best practices into practice from the get-go.

The guide that shaped this project was *Flask for Real Projects: A Hands-On Guide to Building Modern Python Web Applications* by Calissa Corinne. From there, I added PostgreSQL as the database, used Bootstrap 5 with the "sketchy" Bootswatch theme for the UI, and deployed it on DigitalOcean — where I got to use one of my favorite distros. The app currently runs on a Fedora server behind Nginx with HTTPS via Let's Encrypt.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.14, Flask, SQLAlchemy 2.0, Flask-Migrate (Alembic) |
| WSGI Server | Gunicorn |
| Frontend | Jinja2, Bootstrap 5 (Bootswatch "sketchy"), custom CSS |
| Database | PostgreSQL |
| Auth | Flask-Login, Flask-WTF (CSRF), Authlib (Google OAuth), hashed API tokens |
| Background Jobs | Valkey (Redis-compatible) + RQ, with retries and telemetry |
| API | Token-based REST API with rate limiting (Flask-Limiter) |
| Server | Fedora, Nginx (reverse proxy + TLS termination), systemd |
| TLS | Let's Encrypt via Certbot (auto-renewal) |
| Hosting | DigitalOcean |

## Features

- **Entry Management** — Create, edit, delete, and publish entries with draft/published status, search, and pagination
- **User Authentication** — Registration, login, password hashing (Werkzeug), and password reset via email tokens
- **OAuth Support** — Sign in with Google via Authlib
- **RESTful API** — Token-based API for programmatic access to entries, with consistent `{data, meta}` and `{error}` response envelopes
- **Admin Dashboard** — Manage users, change roles, delete accounts, and inspect the email outbox
- **Role-Based Access Control** — Member and admin roles enforced via decorator
- **Background Email Delivery** — Durable outbox pattern with RQ workers; emails are retried on failure and deduplicated
- **Rate Limiting** — Per-user (when authenticated) or per-IP rate limits on the API
- **Security Headers** — Content-Security-Policy, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy
- **HTTPS Enforcement** — Application-level redirect based on `X-Forwarded-Proto`, with secure session and remember-me cookies
- **OpenAPI / Swagger UI** — Auto-generated API docs at `/docs/swagger`
- **Structured Logging** — Per-request logging with method, path, status, and duration

## Architecture

┌──────────────┐
│   Browser    │
└──────┬───────┘
│ HTTPS
┌──────▼───────┐      ┌─────────────┐
│    Nginx     │─────▶│   Gunicorn  │──┐
│ (TLS + 80→443│      │  (Flask app)│  │
└──────────────┘      └─────────────┘  │
│
┌──────────┴──────────┐
▼                     ▼
┌──────────┐         ┌──────────┐
│PostgreSQL│         │  Valkey  │
└──────────┘         └────┬─────┘
│
┌────────┴────────┐
▼                 ▼
┌──────────┐      ┌───────────┐
│RQ Worker │      │ Scheduler │
│ (email)  │      │ (cleanup) │
└──────────┘      └───────────┘


**How the pieces talk to each other:**
- **Nginx** terminates TLS, serves static files, and reverse-proxies dynamic requests to Gunicorn
- **Gunicorn** runs the Flask application and handles incoming HTTP requests
- **PostgreSQL** is the durable store for users, entries, tokens, and the email outbox
- **Valkey** is a fast message broker — Flask pushes background tasks (like "send this email") onto a queue, and a separate worker process picks them up so users don't wait
- **RQ Worker** consumes those queued jobs (sending emails, etc.)
- **Scheduler** enqueues periodic maintenance jobs (cleaning up expired tokens, surfacing stale email outbox entries)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/WebArtisan254/autospeed.git
cd autospeed
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Valkey (or Redis)

On Fedora:

```bash
sudo dnf install -y valkey
sudo systemctl enable --now valkey
```

On Debian/Ubuntu (Redis is still the default):

```bash
sudo apt install -y redis-server
sudo systemctl enable --now redis-server
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```bash
AUTOSPEED_ENV=development
AUTOSPEED_SECRET_KEY=your-secret-key
AUTOSPEED_DATABASE_URL=postgresql://user:password@localhost/autospeed
REDIS_URL=redis://localhost:6379/0

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

> The `REDIS_URL` variable is named after the protocol, not the server — Valkey speaks the same protocol, so the same URL works for both.

### 6. Initialize the database

```bash
flask --app wsgi db upgrade
```

### 7. Run the application

In separate terminals:

```bash
# Web server
flask --app wsgi run --debug

# Background worker
python worker.py

# Scheduler (optional; runs hourly maintenance)
python scheduler.py
```

## Production Deployment

AutoSpeed runs in production with:

- **Gunicorn** — WSGI server bound to `127.0.0.1:8000`
- **Nginx** — reverse proxy, TLS termination, static file serving
- **Let's Encrypt** — TLS certificates auto-renewed via `certbot-renew.timer`
- **systemd** — manages Gunicorn, the RQ worker, and the scheduler as separate services
- **PostgreSQL** — production database
- **Valkey** — message broker for background jobs

Production hardening enabled in `ProductionConfig`:
- `SESSION_COOKIE_SECURE` / `HTTPONLY` / `SAMESITE=Lax`
- `REMEMBER_COOKIE_SECURE` / `HTTPONLY` / `SAMESITE=Lax`
- `USE_PROXY_FIX = True` (so Flask trusts `X-Forwarded-*` headers from Nginx)
- `REQUIRE_HTTPS = True` (redirects any non-HTTPS request)
- CORS restricted to the production domain

## API Usage

Generate an API token at `/auth/tokens`, then include it in the `Authorization` header:

```bash
# List your entries
curl -H "Authorization: Bearer YOUR_TOKEN" https://proautotype.com/api/entries

# Create an entry
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Entry", "content": "Hello from the API"}' \
  https://proautotype.com/api/entries
```

Full interactive docs at [`/docs/swagger`](https://proautotype.com/docs/swagger).

## Roadmap

- [x] Custom domain name
- [x] SSL/TLS (HTTPS via Let's Encrypt)
- [x] Background job processing (Valkey + RQ)
- [x] OpenAPI documentation
- [ ] Real SMTP provider integration (currently using a placeholder)
- [ ] Docker containerization
- [ ] Jenkins CI/CD pipeline
- [ ] Full test coverage

## Acknowledgments

- *Flask for Real Projects* by Calissa Corinne — the guide that shaped this project
- Cisco DevNet course at CIAT (California Institute of Applied Technology) — where the journey started

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


