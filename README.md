# PULSE Athletic Club — Membership Site

A Flask website for the club membership card: visitors register, log in, and
view their digital membership card; admins manage tiers and freeze/unfreeze
cards. Built with Flask **blueprints** (`auth`, `main`, `card`, `admin`).

## Structure

```
club_card_site/
├── app/
│   ├── __init__.py       # application factory — wires extensions, security headers, blueprints
│   ├── config.py         # environment-based config (dev/prod/testing)
│   ├── extensions.py     # db, login_manager, csrf, limiter (created here, bound in the factory)
│   ├── models.py         # User, MembershipCard, AuditLog
│   ├── utils.py          # audit logging, member-number generator
│   ├── cli.py            # `flask create-admin` command
│   ├── auth/              # register, login, logout
│   ├── main/               # public landing page
│   ├── card/               # the logged-in member's card view
│   ├── admin/               # tier management, freeze/unfreeze
│   ├── templates/
│   └── static/{css,js}
├── run.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste the output into SECRET_KEY in .env

# For local testing over plain http (no HTTPS), also set in .env:
# SESSION_COOKIE_SECURE=false
# FLASK_ENV=development

export FLASK_APP=run.py          # Windows (cmd): set FLASK_APP=run.py
flask create-admin               # creates your first admin account

python run.py                    # visit http://127.0.0.1:5000
```

In production, run behind a real HTTPS-terminating server, e.g.:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```
and put nginx/Caddy in front of it for TLS.

## Security measures included

- **Passwords**: hashed with bcrypt (never stored in plain text or reversibly encrypted).
- **CSRF protection**: every form (`Flask-WTF`) carries a token; state-changing
  routes only ever accept POST.
- **Session cookies**: `HttpOnly`, `SameSite=Lax`, `Secure` in production —
  cookies can't be read by JS and won't leave over plain HTTP.
- **Security headers & forced HTTPS**: via `Flask-Talisman` — a strict
  Content-Security-Policy (no inline scripts, nothing from third-party
  hosts), HSTS, `X-Frame-Options: DENY` (blocks clickjacking), no `Server` header leak.
- **Rate limiting**: `Flask-Limiter` throttles login (10/min) and
  registration (10/hour) to slow down brute-force and mass-signup scripts.
- **Account lockout**: 5 failed logins locks the account for 15 minutes.
- **Generic auth errors**: login never reveals whether the email or the
  password was wrong (blocks user enumeration).
- **SQL injection**: all queries go through SQLAlchemy's ORM with bound
  parameters — no raw string-built SQL anywhere.
- **XSS**: Jinja2 auto-escapes all template output by default; nothing
  in this app disables that.
- **Open-redirect guard**: the post-login `next` redirect only accepts a
  same-site relative path.
- **Unguessable identifiers**: each card carries a random `public_token`
  (not the sequential database id) for anything exposed externally (e.g. a
  future QR check-in link), so cards can't be enumerated by guessing IDs.
- **Admin routes**: gated by a real `is_admin` flag, return a plain 404 (not
  403) to non-admins so the admin area's existence isn't even confirmed.
- **Audit log**: logins, lockouts, and admin tier/freeze actions are
  recorded with actor, timestamp, and IP.
- **No secrets in code**: `SECRET_KEY`, DB URL, etc. come from environment
  variables (`.env`, gitignored); the app refuses to start in production
  without a real `SECRET_KEY`.
- **Generic error pages**: 403/404/429/500 show a plain message, never a
  stack trace or internal detail.
- **Request body cap**: 4 MB max, to blunt oversized-payload abuse.

## Before going live

- Swap SQLite for Postgres/MySQL (`DATABASE_URL` in `.env`).
- Point `RATELIMIT_STORAGE_URI` at Redis instead of in-memory storage (in-memory
  limits reset on restart and don't work across multiple worker processes).
- Put it behind HTTPS (nginx/Caddy + Let's Encrypt, or your host's managed TLS).
- Consider adding email verification and a "forgot password" flow (not
  included here) before opening registration to the public.
