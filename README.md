# AutoSpeed 🚗⚡

AutoSpeed is a full-stack Flask web application for creating, managing, and publishing entries. Built using the application factory pattern with a clean blueprint architecture, it features user authentication, role-based access control, a RESTful API, and an admin dashboard.

**Live:** [http://134.122.126.159](http://134.122.126.159)

## About

AutoSpeed started as a project during the **Cisco DevNet** course at the **California Institute of Applied Technology (CIAT)** and was built following *Flask for Real Projects: A Hands-On Guide to Building Modern Python Web Applications* by **Calissa Corinne**. What began as a learning exercise grew into a fully deployed web application running on a Fedora server on DigitalOcean.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, SQLAlchemy, Gunicorn |
| Frontend | HTML, CSS, Bootstrap 5, Jinja2 |
| Database | PostgreSQL |
| Auth | Flask-Login, OAuth, API Tokens |
| Server | Fedora, Nginx, systemd |
| Hosting | DigitalOcean |

## Features

- **Entry Management** — Create, edit, delete, and publish entries with draft/published status and tagging
- **User Authentication** — Registration, login, password hashing (scrypt), email verification, and password reset
- **OAuth Support** — Sign in with third-party providers
- **RESTful API** — Token-based API access for programmatic entry management
- **Admin Dashboard** — Manage users, monitor activity, and maintain the platform
- **Role-Based Access Control** — Separate member and admin roles
- **Rate Limiting** — Protects against brute force and abuse
- **Security Headers** — Content-Security-Policy, X-Frame-Options, and more

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/WebArtisan254/autospeed.git
cd autospeed

2. Create and activate a virtual environment
bash

python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\Activate

3. Install dependencies
bash

pip install -r requirements.txt

4. Set up environment variables

Create a .env file in the project root with your configuration:

FLASK_APP=wsgi
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/autospeed

5. Initialize the database
bash

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

6. Run the application
bash

flask --app wsgi run --debug

Production Deployment

AutoSpeed runs in production with the following setup:

    Gunicorn as the WSGI server (2 workers, bound to 127.0.0.1:8000)
    Nginx as a reverse proxy handling static files and client connections
    systemd managing the application as a service
    PostgreSQL as the production database

Roadmap

    Custom domain name
    SSL/TLS (HTTPS)
    Docker containerization
    CI/CD pipeline

Acknowledgments

    Flask for Real Projects by Calissa Corinne — the guide that shaped this project
    Cisco DevNet course at CIAT (California Institute of Applied Technology) — where the journey started

License

This project is licensed under the MIT License.

