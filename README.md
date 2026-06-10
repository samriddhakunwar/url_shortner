# URL Shortener

A URL shortener built with Django. You sign up, paste in a long link, and get back a short one that redirects to the original. You can also give links a custom name, set them to expire, generate a QR code, and see how many times each one has been clicked.

There's a normal web interface for day-to-day use, and a REST API underneath it (with Swagger docs) if you'd rather hit it programmatically.

Live demo: https://url-shortner-sh8m.vercel.app

## What it does

- Register / log in / log out
- Shorten any URL — short codes are generated with base62 so they stay compact
- Pick your own custom alias instead of the auto-generated code
- Set an expiry date so a link stops working after a certain time
- QR code for every short link
- Click tracking — see how many times each link was used and when it was last clicked
- A list view to manage everything you've made (edit or delete)
- Basic analytics page that ranks your links by clicks

Only logged-in users can create or manage links, and you only ever see your own.

## Tech

- Django + Django REST Framework
- JWT auth for the API (SimpleJWT), session auth for the web pages
- SQLite for local dev, PostgreSQL in production
- WhiteNoise for serving static files
- Swagger / ReDoc for API docs (drf-yasg)

## Running it locally

You'll need Python 3.10+.

```bash
# clone and enter the project
git clone https://github.com/samriddhakunwar/url_shortner.git
cd url_shortner

# set up a virtual environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

Make a `.env` file in the project root with a secret key:

```
DJANGO_SECRET_KEY=put-any-random-string-here
```

Then run the migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000, register an account, and you're in.

If you don't set `DATABASE_URL`, it falls back to a local SQLite file, so there's nothing else to configure for development.

## Environment variables

| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | Any random string. |
| `DATABASE_URL` | no | Postgres connection string. Leave it out locally and it uses SQLite. |
| `ALLOWED_HOSTS` | no | Comma-separated list. Defaults to `*`. |

## The API

If you want to use the API directly, the docs are at `/swagger/` (or `/redoc/`).

Auth is JWT-based. Log in to get a token, then send it as a `Bearer` header on the URL endpoints.

```
POST /api/auth/register/     create an account
POST /api/auth/login/        get access + refresh tokens
POST /api/auth/logout/       blacklist the refresh token

GET    /api/urls/            list your short URLs
POST   /api/urls/            create one
PATCH  /api/urls/{id}/       edit
DELETE /api/urls/{id}/       delete

GET  /r/{short_code}/        the actual redirect (and where clicks get counted)
```

Logging in uses your email and password, since accounts are keyed on email rather than username.

## A note on short codes

The short codes come from base62-encoding a microsecond timestamp, which keeps them short and avoids predictable sequential IDs. If two ever collided, there's a small retry loop that nudges the value until it's unique — in practice this basically never fires.

## Deploying

The repo is set up to deploy to Vercel as-is (there's a `vercel.json` and the WSGI entrypoint is wired up for it). Two things matter on a serverless host:

1. Use a real database — set `DATABASE_URL` to a Postgres instance (Neon's free tier works well). SQLite won't survive between requests on Vercel.
2. Set `DJANGO_SECRET_KEY` in the project's environment variables.

Static files are collected into `staticfiles/` and served by WhiteNoise, and QR codes are stored as base64 in the database rather than as files, so there's no filesystem dependency.

## Project layout

```
config/       project settings, root URLs, WSGI
accounts/     custom user model + auth API
shortener/    the core models, short-code logic, QR generation, redirect + API
frontend/     server-rendered pages (templates, views, forms)
```
