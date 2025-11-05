# 🚀 pyshop‑api
### Full-Stack E-Commerce Platform - Production-Ready with Cloud Infrastructure

![CI](https://github.com/luminarics/pyshop-api/actions/workflows/python-tests.yml/badge.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ed?logo=docker&logoColor=white) ![Coverage](https://img.shields.io/badge/Coverage-90%25+-brightgreen) ![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js) ![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform) 

---

**A complete, enterprise-grade e-commerce platform with FastAPI backend, Next.js frontend, and cloud infrastructure.** Features full shopping cart & checkout, order management, JWT authentication, real-time monitoring, AWS/Azure Terraform deployments, and production-ready Docker orchestration.

##

```bash
git clone https://github.com/luminarics/pyshop-api.git && cd pyshop-api
cp .env.example .env              # edit values or keep the sane defaults
docker compose up --build         # API → http://localhost:8000 ⚡️
```

| URL        | What                                               |
| ---------- | -------------------------------------------------- |
| `:3000`    | Next.js Frontend (PyShop e-commerce UI)            |
| `/docs`    | Swagger‑UI (OpenAPI)                               |
| `/redoc`   | ReDoc docs                                         |
| `/health`  | Liveness/DB check                                  |
| `/metrics` | Prometheus metrics (scraped by the prom container) |
| `:9090`    | Prometheus UI                                      |
| `:3002`    | Grafana (admin / admin, auto-configured)           |

---

### 🚀 Core Features

#### 🎯 Backend (FastAPI)
* **FastAPI 0.115 + SQLModel** - 100% async with PostgreSQL (asyncpg)
* **FastAPI-Users** - JWT authentication with refresh tokens
* **Complete Shopping Cart System**
  - Guest cart support (session-based, cookie management)
  - User cart persistence and migration
  - Cart validation and conversion to orders
* **Order Management System**
  - Full order lifecycle (pending → confirmed → processing → shipped → delivered)
  - Payment status tracking (pending, completed, failed, refunded)
  - Order history and detailed tracking
  - Shipping information management
* **Product Catalog** - Advanced pagination, filtering, and search
* **Prometheus /metrics** + auto-provisioned Grafana dashboards

#### 🎨 Frontend (Next.js 15)
* **15+ Production Pages** - Cart, Checkout, Orders, Products, Categories, Deals, Wishlist, Settings, Profile, Dashboard, Contact, About
* **TypeScript + Tailwind CSS + shadcn/ui** - Type-safe, responsive design system
* **Dynamic Shopping Cart** - Real-time item count updates in header
* **Protected Routes** - JWT authentication with automatic token refresh
* **React Query** - Optimized data fetching, caching, and state management
* **Complete Checkout Flow** - Multi-step with validation and order confirmation

#### ☁️ Infrastructure & DevOps
* **Terraform IaC** - AWS (ECS, Aurora Serverless, ALB, CloudWatch) & Azure deployments
* **Docker + Compose** - Multi-service orchestration (API, DB, Frontend, Prometheus, Grafana)
* **GitHub Actions CI/CD** - Automated testing, linting, Docker image publishing to GHCR
* **Alembic Migrations** - Auto-generate & run on startup
* **Development Scripts** - One-command setup, testing, and database management

#### ✅ Quality & Testing
* **≥90% Test Coverage** - Pytest with async support
* **E2E Testing** - Playwright for full user journey validation
* **Code Quality** - Ruff, Black, MyPy with strict type checking
* **Pre-commit Hooks** - Automated quality checks

### 💎 What Makes This Project Stand Out

* **🏆 Enterprise Architecture** - Clean separation of concerns, SOLID principles, dependency injection
* **⚡ Performance First** - 100% async/await, connection pooling, optimized database queries
* **🔒 Security Focused** - JWT authentication, input validation, SQL injection protection
* **📈 Production Monitoring** - Comprehensive metrics, structured logging, health checks
* **🧪 Quality Assurance** - 90%+ test coverage, strict typing, automated code quality checks
* **🚀 Developer Experience** - Hot reload, comprehensive tooling, clear documentation
* **🔄 CI/CD Ready** - GitHub Actions, pre-commit hooks, automated deployment
* **☁️ Cloud-Ready Infrastructure** - AWS & Azure Terraform modules for production deployment
* **🛒 Complete E-commerce Features** - Full cart, checkout, orders, and product management

Roadmap → [#milestones](#roadmap).

---

## Requirements

* Docker ≥ 25
* Make, if you like the optional helper targets
* Or: Python 3.12 + Poetry for a native setup

---

## Local development (Poetry)

```bash
# Automated setup (recommended)
./scripts/setup.sh               # installs deps, creates .env, starts Docker

# Start development server
./scripts/dev.sh                 # starts DB, runs migrations, starts server with hot reload

# Or manually
poetry install --with dev
export SECRET_KEY=dev123
export DATABASE_URL=sqlite+aiosqlite:///:memory:
poetry run uvicorn app.main:app --reload
```

> **Tip:** SQLite is fine for unit tests; use Postgres in Docker for manual poking.

---

## Environment variables

| Var                           | Default (docker)                               | Required | Notes                                   |
| ----------------------------- | ---------------------------------------------- | -------- | --------------------------------------- |
| `SECRET_KEY`                  | *none*                                         | ✅        | JWT signing key – must be long & random |
| `DATABASE_URL`                | `postgresql+asyncpg://app:app@db:5432/fastapi` |          | SQLAlchemy URL                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                           |          | JWT TTL                                 |

See `.env.example` for a full list.

---

## Auth flow (curl cheatsheet)

```bash
# 1 — Register
curl -X POST http://localhost:8000/auth/register \
     -H 'Content-Type: application/json' \
     -d '{"email":"[email protected]","password":"hunter2","username":"deni"}'

# 2 — Login (form‑encoded!)
curl -X POST http://localhost:8000/auth/jwt/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=[email protected]&password=hunter2'

# 3 — Hit a protected route
TOKEN="$(jq -r .access_token <<< "$RESPONSE")"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/profile
```

---

## Running tests & linters

```bash
# Using helper scripts (recommended)
./scripts/test.sh                # run unit tests
./scripts/test.sh --e2e          # run all tests including E2E
./scripts/test.sh --coverage     # run with coverage report
./scripts/lint.sh                # run all linters
./scripts/lint.sh --fix          # auto-fix issues

# Or manually inside venv / poetry shell
pytest -q -m "not e2e"       # unit tests only
pytest tests/e2e -m e2e      # E2E tests (requires running server)
ruff .                       # lint
black --check .              # formatting
mypy app tests               # static types
```

The CI workflow mirrors the same steps with automated testing.

---

## Migrations

```bash
# Using helper script (recommended)
./scripts/db.sh migrate          # run pending migrations
./scripts/db.sh revision "msg"   # create new migration
./scripts/db.sh rollback         # rollback one migration
./scripts/db.sh reset            # reset database (WARNING: deletes all data)
./scripts/db.sh shell            # open PostgreSQL shell

# Or manually
alembic revision --autogenerate -m "add product table"
alembic upgrade head
```

The Docker image runs `alembic upgrade head` at start‑up so containers come up with the latest schema.

---

## Monitoring

* **Prometheus** scrapes `http://api:8000/metrics` every 15 s (see `monitoring/prometheus.yml`).
* **Grafana** auto-provisions with pre-configured Prometheus datasource and PyShop API dashboard
  - Dashboard includes: Request rates, response times (p50/p90/p95/p99), status codes, error rates, memory usage
  - Configuration in `monitoring/grafana/provisioning/` (datasources + dashboards)
  - Access at http://localhost:3002 (admin/admin)
  - No manual import needed - ready on first startup!

![Grafana screenshot](./docs/grafana.png)

---

## Project layout

```
app/
 ├── routers/             # API endpoints
 ├── core/                # Settings, security, utils
 ├── models/              # SQLModel tables & Pydantic schemas
 ├── auth/                # Authentication logic
 ├── database.py          # Database connection
 └── main.py              # FastAPI factory & router mounting
tests/
 ├── e2e/                 # Playwright E2E tests
 └── *.py                 # Unit tests
scripts/
 ├── setup.sh             # Development environment setup
 ├── dev.sh               # Start development server
 ├── test.sh              # Run tests
 ├── lint.sh              # Run linters
 └── db.sh                # Database management
.github/workflows/
 ├── ci.yml               # CI pipeline
 └── cd.yml               # CD pipeline
docs/
 ├── API.md               # API documentation
 └── DEPLOYMENT.md        # Deployment guide
monitoring/
 ├── prometheus.yml
 ├── grafana.json         # Dashboard definition
 └── grafana/
     └── provisioning/    # Auto-provisioning configs
         ├── datasources/ # Prometheus datasource
         └── dashboards/  # Pre-configured dashboards
Dockerfile
docker-compose.yml
alembic/
```

---

## Roadmap

### ✅ Completed
* ✅ Deploy infrastructure to **AWS/Azure** via Terraform
* ✅ Implement complete shopping cart and checkout system
* ✅ Build production-ready Next.js frontend with 15+ pages
* ✅ Auto-provision Grafana monitoring dashboards
* ✅ Guest cart support with session management
* ✅ Order management system with full lifecycle tracking

### 🚀 In Progress / Planned
* 💳 Payment gateway integration (Stripe/PayPal)
* ⭐ Product reviews and ratings system
* 🔍 Advanced product search with Elasticsearch
* 📧 Email notifications for order updates
* 🛠️ Contribute PRs to the FastAPI ecosystem
---

## Contributing

PRs, issues and *polite rants* are welcome. Before you open a PR:

1. Create a branch off **`main`**.
2. `pre-commit run --all-files` (installs hooks automatically).
3. Make sure `pytest` and `mypy` are 💚 locally.

If you’re new to FastAPI, check the [FastAPI docs](https://fastapi.tiangolo.com/) and [SQLModel docs](https://sqlmodel.tiangolo.com/) first — then hack away.

---

## License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.
