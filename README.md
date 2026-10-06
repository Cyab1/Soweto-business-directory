# Kasi Konekt (Soweto Business Directory)

A Django REST Framework API for discovering, verifying and claiming township businesses, starting with Soweto, South Africa. Imported listings start as *unclaimed*; owners claim them, and staff review each claim before ownership changes hands.

## Features

- Business listings with categories, services, price range, WhatsApp, social links and coordinates.
- Reviews (one per user per business).
- Search and filtering by name, address, category, owner, status and verification.
- **Nearby search**: distance-sorted results within a radius, verified businesses first.
- **Verification**: staff can verify or unverify a listing, and every action is written to an audit log.
- **Claim flow**: any logged-in user can request ownership of an unclaimed listing. Staff approve or reject it, and one approval closes all other pending claims on that listing.
- **CSV import** for bulk-loading unclaimed listings (safe to re-run).
- JWT authentication with self-service registration.
- Rate limiting on the abuse-prone endpoints.
- Interactive API docs (OpenAPI / Swagger).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Auth | JWT (`djangorestframework-simplejwt`) |
| API docs | `drf-spectacular` |
| Database | SQLite (development), PostgreSQL (production) |
| Serving | gunicorn, WhiteNoise |
| Frontend | React + TypeScript + Tailwind, built in Lovable (separate project: *add link*) |

## Getting Started

1. Clone the repository:

```bash
   git clone https://github.com/Cyab1/Soweto-business-directory.git
   cd Soweto-business-directory
```

2. Create and activate a virtual environment:

```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
   pip install -r requirements.txt
```

4. Create a `.env` file in the project root (see [Configuration](#configuration)). For local development all values are optional.

5. Apply migrations and create an admin account:

```bash
   python manage.py migrate
   python manage.py createsuperuser
```

6. Run the server:

```bash
   python manage.py runserver
```

The API is now at `http://127.0.0.1:8000/api/` and the docs at `http://127.0.0.1:8000/api/docs/`.

## Configuration

Settings are read from environment variables (or `.env` locally). Never commit `.env`.

| Variable | Purpose | Local default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Signs sessions and JWTs. Use a long random value (64+ characters) in production. | insecure dev key |
| `DJANGO_DEBUG` | `True` or `False`. Must be `False` in production. | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | `127.0.0.1,localhost` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins (exact, with `https://`, no trailing slash) | `localhost:3000` |
| `CSRF_TRUSTED_ORIGINS` | Needed for the admin over HTTPS | empty |
| `DATABASE_URL` | PostgreSQL connection string. If unset, SQLite is used. | unset |

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## API Overview

Full, always-current documentation is at `/api/docs/` (schema at `/api/schema/`).

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Create an account (`username`, `email`, `password`) |
| POST | `/api/token/` | Log in, returns `access` and `refresh` tokens |
| POST | `/api/token/refresh/` | Get a new access token |
| GET | `/api/me/` | The current user, including `is_staff` |

Send `Authorization: Bearer <access token>` on authenticated requests.

### Directory

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/categories/` | public | List categories |
| GET | `/api/businesses/` | public | List businesses. Filters: `category`, `owner`, `is_verified`, `status`. Search: `?search=` |
| POST | `/api/businesses/` | logged in | Create a listing (you become the owner) |
| GET | `/api/businesses/nearby/?lat=&lng=&radius_km=` | public | Distance-sorted results, verified first |
| GET/POST | `/api/reviews/` | read public, write logged in | Reviews |

### Verification and claims

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/businesses/{id}/verify/` | staff | Mark a listing verified |
| POST | `/api/businesses/{id}/unverify/` | staff | Remove verification |
| POST | `/api/businesses/{id}/claim/` | logged in | Request ownership of an unclaimed listing (`evidence`, `contact_phone`) |
| GET | `/api/my-claims/` | logged in | Your own claim requests |
| GET | `/api/claims/` | staff | Pending claims |
| POST | `/api/claims/{id}/approve/` | staff | Approve, assigns the owner |
| POST | `/api/claims/{id}/reject/` | staff | Reject, with an optional `note` |

### Rate limits

| Scope | Limit |
|---|---|
| Anonymous | 100/hour |
| Authenticated | 1000/hour |
| Reviews | 10/hour |
| Claims | 5/hour |
| Registration | 10/hour |

Exceeding a limit returns HTTP 429.

## Importing Businesses

Bulk-load listings from a CSV as unclaimed businesses:

```bash
python manage.py import_businesses path/to/file.csv --dry-run   # preview, saves nothing
python manage.py import_businesses path/to/file.csv
```

Required columns: `external_id`, `name`, `category`, `address`.
Optional columns: `contact_info`, `services`, `whatsapp`, `website_url`, `instagram`, `facebook`, `price_range`, `latitude`, `longitude`.

The import is idempotent: rows are matched on `source` plus `external_id`, so re-running updates unclaimed listings instead of duplicating them. Listings already claimed by an owner are never overwritten. Rows without coordinates are imported but reported, because they cannot appear in nearby search.

Only import data you have the right to use. Business contact details can be personal information under POPIA, so keep real data files out of git.

## Testing

```bash
python manage.py test listings
```

The suite covers the claim flow, staff review, privilege-escalation attempts (self-verifying, editing ownerless listings, self-registering as staff), registration and per-user claim visibility.

## Security Notes

- `is_verified`, `status`, `source` and `external_id` are read-only through the public API.
- Staff-only actions are enforced on the server, not just hidden in the UI.
- Claim approval runs in a database transaction and rechecks that the listing is still unclaimed.
- Production settings (HTTPS redirect, secure cookies, HSTS) switch on automatically when `DJANGO_DEBUG=False`.
- Uploaded media is stored on local disk. On hosts with ephemeral storage it will not persist, so move uploads to object storage (e.g. S3) before relying on them.

## Roadmap

- Owner dashboard: edit listings, upload logos and photos.
- Move media storage to S3.
- POPIA compliance checklist: consent, data minimisation, listing deletion.
- Threat model and case study write-up.

## License

MIT License. See `LICENSE`.