# Atlan Backend Challenge (2025)

This repository contains a FastAPI-based backend service for managing events, bookings, and users. It demonstrates core features such as event creation, ticket booking with concurrency-safe inventory handling, user management, and analytics.

---

## Features

* **User Management**: Create, list, and delete users.
* **Event Management**: Create, update, list, and delete events.
* **Booking System**: Book and cancel tickets with idempotency support.
* **Analytics**: View total bookings and utilization per event.
* **Database**: PostgreSQL with materialized views for analytics.

---

## Tech Stack

* **Python 3.11**
* **FastAPI**
* **PostgreSQL**
* **Docker & Docker Compose**
* **asyncpg** for async database operations

---

## Getting Started (Local Development)

### Prerequisites

* Docker & Docker Compose installed
* Python 3.11 (optional if using Docker)
* `git` installed

---

### Clone the repository

```bash
git clone https://github.com/pranavchachra1702/Stellar_Events_Backend.git
cd Stellar_Events_Backend
```

### Environment Variables

Create a `.env` file for local development based on `.env.example`:

```env
DATABASE_URL=postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>
INIT_DB=true
```

---

### Running with Docker Compose

The repository includes a `docker-compose.yml` for local development:

```bash
docker-compose up --build
```

This will start:

* **PostgreSQL** database on port `5432`
* **FastAPI backend** on port `8000`

You can access the API docs at:

```
http://localhost:8000/docs
```

---

### Database

The first time you run, the database schema will be initialized automatically if `INIT_DB=true`.

Default credentials in `docker-compose.yml` for local development:

```yaml
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_DB: evently
```

---

### API Endpoints (Overview)

#### Users

* `POST /users/` — create user
* `GET /users/` — list users
* `GET /users/{id}` — get user by ID
* `DELETE /users/{id}` — delete user

#### Events

* `POST /events/` — create event
* `GET /events/` — list events
* `GET /events/{id}` — get event by ID
* `PUT /events/{id}` — update event
* `DELETE /events/{id}` — delete event

#### Bookings

* `POST /bookings/` — book tickets
* `POST /bookings/{id}/cancel` — cancel booking
* `GET /bookings/user/{user_id}` — list user bookings

#### Analytics

* `GET /admin/analytics` — get event booking stats

> Full OpenAPI docs are available at `/docs` when running locally.
