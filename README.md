# Tricky-URL-Shortener

REST API for URL shortener, with main "feature" that crawls passed URL's and extracts images/emails for further processing.

## Stack

App is wrapped around Python 3.9 with:

- FastAPI
- PyTest
- SQLAlchemy
- PostgreSQL
- Docker
- Alembic
- AWS S3
- Mailog
- Beautifulsoup4
- Jinja2

Run it with

```
docker-compose up
```
