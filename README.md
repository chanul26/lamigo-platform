# 🚚 LamiGo - Last-Mile Delivery Optimization Platform

LamiGo is a multi-stack platform for optimizing last-mile delivery logistics in Sri Lanka. It consists of a **FastAPI backend**, a **Flutter mobile app** for drivers, and **Next.js web portals** for station staff and customers.

**SDGP CS-155 Project**

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Folder Structure](#-folder-structure)
- [How It All Works](#-how-it-all-works)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Getting Started (Docker)](#-getting-started-docker-first)
- [Development Workflow (Protected Branch)](#-development-workflow-strict)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Useful Commands Cheat Sheet](#-useful-commands-cheat-sheet)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Development Tips](#-development-tips)

---

## 🎯 Project Overview

| Component | Purpose |
|-----------|---------|
| **Backend** | REST API for packages, drivers, stations; CORS-enabled for web portals; placeholder for ML route optimization. |
| **Mobile App** | Flutter app for delivery drivers (Android/iOS). |
| **Station Manager** | Next.js dashboard for station staff: manage packages, drivers, trips, settlements. |
| **Customer Portal** | Next.js app for customers to track deliveries. |

All frontends talk to the same backend at `http://localhost:8000`.

---

## 📁 Folder Structure

```
lamigo-platform/
│
├── README.md                    # This file
├── .gitignore                   # Multi-stack ignore rules
│
├── backend/                     # Python FastAPI Backend
│   ├── main.py                  # Legacy entry (imports from app/)
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── config/
│   │   └── serviceAccountKey.json  # Firebase service account (git-ignored)
│   ├── scripts/
│   │   └── bootstrap_admin.py   # Multi-tenant setup script
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app, CORS, router registration
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py              # API router
│       │       └── endpoints/
│       │           ├── __init__.py
│       │           ├── packages.py          # Package endpoints
│       │           └── drivers.py           # Driver endpoints
│       ├── db/
│       │   ├── __init__.py
│       │   ├── base.py          # SQLAlchemy declarative base
│       │   └── models.py        # Organization & User multi-tenant models
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── package.py       # Package Pydantic models
│       │   ├── driver.py        # Driver Pydantic models
│       │   └── station.py      # Station Pydantic models
│       └── services/
│           ├── __init__.py
│           └── optimization.py  # ML placeholder (route optimization)
│
├── mobile-app/                  # Flutter Driver Application
│   ├── pubspec.yaml             # Dart/Flutter dependencies
│   ├── pubspec.lock
│   ├── lib/                     # Dart source code
│   │   ├── main.dart
│   │   └── login_screen.dart
│   ├── test/
│   │   └── widget_test.dart
│   └── android/                 # Android platform config
│       ├── app/
│       │   ├── build.gradle.kts
│       │   └── src/main/...
│       ├── build.gradle.kts
│       ├── settings.gradle.kts
│       └── gradle/
│
├── web-portals/                 # Next.js Web Applications
│   │
│   ├── station-manager/         # Staff dashboard (port 3000)
│   │   ├── package.json
│   │   ├── app/
│   │   │   ├── layout.tsx       # App shell + sidebar
│   │   │   ├── page.tsx         # Dashboard
│   │   │   ├── globals.css      # Design system
│   │   │   ├── drivers/page.tsx
│   │   │   ├── packages/page.tsx
│   │   │   ├── trips/page.tsx
│   │   │   ├── ongoing-trips/page.tsx
│   │   │   ├── settlements/page.tsx
│   │   │   ├── incidents/page.tsx
│   │   │   └── settings/page.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   │   ├── LayoutWithOptionalSidebar.tsx  # Layout wrapper
│   │   │   └── SplashScreen.tsx # Loading screen
│   │   ├── lib/
│   │   │   ├── api.ts           # API client for backend
│   │   │   └── firebase.ts      # Firebase config & auth client
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript types (mirror Pydantic)
│   │   └── public/
│   │
│   └── customer-portal/         # Customer tracking (port 3001)
│       ├── package.json
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   └── globals.css
│       └── public/
│
└── docs/                        # Project documentation
    └── .gitkeep
```

---

## 🔄 How It All Works

```
                    ┌──────────────────────────────────────────┐
                    │     LamiGo FastAPI Backend                │
                    │     http://localhost:8000                 │
                    │     /api/v1/packages, /drivers, etc.       │
                    │     Multi-tenant: Organizations + Users     │
                    └──────────────────┬───────────────────────┘
                                       │
         ┌─────────────────────────────┼──────────────────────────────┐
         │                             │                              │
         ▼                             ▼                              ▼
┌───────────────────┐        ┌──────────────────┐        ┌─────────────────┐
│  Station Manager  │        │  Customer Portal │        │  Mobile App     │
│  (Next.js, React) │        │  (Next.js, React)│        │  (Flutter)      │
│  Firebase Auth    │        │  Firebase Auth   │        │  Drivers        │
│  :3000            │        │  :3001           │        │  Android/iOS    │
└───────────────────┘        └──────────────────┘        └─────────────────┘
         │                              │
         └──────────────────┬───────────┘
                            │
              ┌─────────────────────────────┐
              │  Firebase Authentication    │
              │  (Multi-Tenant Enabled)     │
              └─────────────────────────────┘
```

- **Backend**: Single FastAPI app with multi-tenant support (Organizations & Users). CORS allows `localhost:3000` and `localhost:3001`. Serves packages, drivers, health; ML optimization is a placeholder. Uses PostgreSQL with SQLAlchemy ORM.
- **Firebase**: Multi-tenant authentication for both web portals and backend. Service account key required for server-side operations (bootstrap_admin.py).
- **Station Manager**: Uses `lib/api.ts` to call the backend; `lib/firebase.ts` for auth. Types in `types/index.ts` match Pydantic schemas.
- **Customer Portal**: Intended for tracking; can use same API (e.g. by tracking number). Firebase auth support.
- **Mobile App**: Flutter UI; will call same REST API for driver workflows.

---

## 🛠️ Tech Stack & Dependencies

### Backend (Python)

| Package | Version | Purpose |
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ≥0.128.0 | Web framework |
| uvicorn | ≥0.40.0 | ASGI server |
| pydantic | ≥2.12.0 | Request/response models |
| sqlalchemy | ≥2.0.0 | Multi-tenant ORM |
| firebase-admin | ≥6.0.0 | Firebase server-side auth |
| pandas | ≥2.0.0 | Data/ML (future) |
| numpy | ≥1.26.0 | ML (future) |
| python-dotenv | ≥1.0.0 | Env config |
| python-multipart | ≥0.0.9 | Form/data |
| httpx | ≥0.27.0 | HTTP client (testing) |

**Install:** `pip install -r backend/requirements.txt`

### Mobile App (Flutter / Dart)

| Package | Version | Purpose |
|---------|---------|---------|
| Dart SDK | ^3.10.4 | Language |
| flutter | sdk | Framework |
| cupertino_icons | ^1.0.8 | Icons |
| flutter_lints | ^6.0.0 | Linting (dev) |

**Install:** `cd mobile-app && flutter pub get`

### Station Manager (Next.js)

| Package | Version | Purpose |
|---------|---------|---------|
| next | 16.1.6 | Framework |
| react | 19.2.3 | UI |
| react-dom | 19.2.3 | UI |
| firebase | ^12.8.0 | Auth & real-time features |
| lucide-react | ^0.563.0 | Icons |
| tailwindcss | ^4 | Styling |
| typescript | ^5 | Type checking |
| eslint, eslint-config-next | 16.1.6 | Linting |

**Install:** `cd web-portals/station-manager && npm install`

### Customer Portal (Next.js)

| Package | Version | Purpose |
|---------|---------|---------|
| next | 16.1.6 | Framework |
| react | 19.2.3 | UI |
| react-dom | 19.2.3 | UI |
| firebase | ^12.8.0 | Auth & real-time features |
| tailwindcss | ^4 | Styling |
| typescript | ^5 | Type checking |
| eslint, eslint-config-next | 16.1.6 | Linting |

**Install:** `cd web-portals/customer-portal && npm install`

---

## �️ Database Schema (Multi-Tenant)

LamiGo uses PostgreSQL with SQLAlchemy ORM for multi-tenant support:

### Organization
Tenant organization (e.g., "CityPack" delivery company)
- `id` (Integer, PK, auto-increment)
- `name` (String, unique) – Organization name
- `created_at` (DateTime) – Creation timestamp
- **Relations:** `users` (1-to-many)

### User
User linked to Firebase UID and an organization with role
- `id` (Integer, PK, auto-increment)
- `firebase_uid` (String, unique) – Firebase authentication UID
- `org_id` (Integer, FK) – Links to Organization
- `role` (String) – e.g., `SUPER_ADMIN`, `ADMIN`, `STAFF`
- `email` (String) – User email
- `created_at` (DateTime) – Creation timestamp
- **Relations:** `organization` (Many-to-1)

**Setup:** Run `python scripts/bootstrap_admin.py` to create the initial CityPack organization and Super Admin user.

---

## 🚀 Getting Started (Docker-First)

The project runs on **Docker**. You don’t need to install Python or PostgreSQL locally—containers provide everything.

### 🐳 Prerequisites

1. **Install Docker Desktop:** [Download here](https://www.docker.com/products/docker-desktop/)
2. **Start it:** Open Docker Desktop and ensure it’s running.

### ▶️ The only command you need

From the **project root** (`lamigo-platform/`):

```bash
docker compose up
```

This starts:

- **FastAPI Backend** → http://localhost:8000 (API docs: http://localhost:8000/docs)
- **PostgreSQL Database** → `localhost:5432` (used by the backend)

Stop with `Ctrl+C` or run `docker compose down`.

---

## ⚠️ Development Workflow (Strict)

> **The `dev` branch is PROTECTED.**  
> Direct pushes to `dev` will **fail**. Follow the flow below.

| Step | What to do |
|------|------------|
| 1️⃣ | Create a new branch from `dev`: `git checkout -b feature/your-feature` |
| 2️⃣ | Push your changes: `git push origin feature/your-feature` |
| 3️⃣ | Open a **Pull Request** into `dev` on GitHub. |
| 4️⃣ | Wait for the **CI/CD Robot** to pass (green check on the PR). |
| 5️⃣ | Merge the PR (squash or merge commit as per team rules). |

No merging until CI is green.

---

## 🤖 CI/CD Pipeline

We use a **GitHub Action** that runs on every Pull Request:

- **Workflow file:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- **What it does:** Builds the Docker image and checks that the backend container starts. If the build or startup fails, the PR shows a red X—fix the issue before merging.

---

## 📋 Useful Commands (Cheat Sheet)

| Goal | Command |
|------|--------|
| **Start app** | `docker compose up` |
| **Rebuild** (e.g. after adding packages to `requirements.txt`) | `docker compose up --build` |
| **Reset database** (nuclear option – deletes all data for a fresh start) | `docker compose down -v` then `docker compose up` |
| **Create Super Admin** (CityPack org + Firebase user) | `docker compose exec backend python scripts/bootstrap_admin.py` |

Bootstrap requires `backend/.env` with `DATABASE_URL` and `FIREBASE_SERVICE_ACCOUNT_PATH`; see [Environment Variables](#-environment-variables) and [Firebase service account path](#firebase-service-account-path).

---

## 📦 Multi-Tenant Bootstrap (non-Docker / local)

If you're not using Docker, use a local venv and run `python scripts/bootstrap_admin.py` from `backend/` after setting `backend/.env` (see [Environment Variables](#-environment-variables) and [Firebase service account path](#firebase-service-account-path)). The long step-by-step below is kept for reference.

**1. Set up the environment**  
You must be inside the `backend` folder and have your virtual environment (“bubble”) activated. The bubble starts empty—install dependencies so the script can find `python-dotenv`, `sqlalchemy`, `firebase-admin`, etc.

```bash
cd backend
source .venv/bin/activate   # or: source venv/bin/activate   # macOS/Linux
# .venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -r requirements.txt
```

**2. Run the Multi-Tenant Bootstrap**  
This creates the CityPack organization and your Super Admin in both Firebase and PostgreSQL. **Copy the one-time password** from the script output.

```bash
python scripts/bootstrap_admin.py
```

**3. Save your progress to GitHub**  
After the script finishes (and you’ve copied your new password), save your work to your feature branch:

```bash
git add .
git status
git commit -m "Multi-tenant bootstrap: CityPack org and Super Admin"
git push origin feature/multi-tenant-auth
```

**4. Cleanup**  
When you’re done working on the backend for now, exit the virtual environment:

```bash
deactivate
```

#### Firebase service account path

The error **`FIREBASE_SERVICE_ACCOUNT_PATH must point to a valid service account JSON file`** means the script can’t find your Firebase “master key” where `.env` says it is. Fix it by aligning the path.

**1. Check your folder structure**  
The service account JSON must live under `backend/`. For LamiGo we use:

- **Folder:** `backend/config/`
- **File name:** `serviceAccountKey.json`  
So the full path is `backend/config/serviceAccountKey.json`. Download the key from [Firebase Console](https://console.firebase.google.com/) → Project Settings → Service accounts → Generate new private key, and save it there.

**2. Update `backend/.env`**  
No extra spaces, no quotes. For the structure above:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=config/serviceAccountKey.json
```

**3. Terminal “proof”**  
From the `backend` folder (with venv active), run:

```bash
ls -la config/serviceAccountKey.json
```

If you get “No such file or directory”, the file is not in the right place or the name is wrong.

**4. Try the bootstrap again**

```bash
python scripts/bootstrap_admin.py
```

**Troubleshooting**

- **Wrong filename:** Ensure the file isn’t `serviceAccountKey.json.json` (double extension).
- **Wrong folder:** Run the script from `backend/`, not from the repo root.
- **Path in .env:** Use a path relative to the backend folder. If the file is in `backend/config/`, use `config/serviceAccountKey.json`.

---


## 📡 API Reference

Base URL: `http://localhost:8000`

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Backend health |
| GET | `/api/health` | API health |

### Packages (`/api/v1/packages`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all packages |
| GET | `/{id}` | Get package by ID |
| GET | `/tracking/{tracking_number}` | Get by tracking number |

### Drivers (`/api/v1/drivers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all drivers |
| GET | `/active` | List active drivers only |
| GET | `/{id}` | Get driver by ID |

---

## 🔧 Environment Variables

Create these only if you need overrides (e.g. different API URL or DB).

### Backend (`backend/.env`)

Copy from `backend/.env.example` and fill in values. Required for multi-tenant bootstrap:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/lamigo
FIREBASE_SERVICE_ACCOUNT_PATH=config/serviceAccountKey.json
```

Place the Firebase service account JSON at `backend/config/serviceAccountKey.json` (see [Firebase service account path](#firebase-service-account-path)).

### Station Manager (`web-portals/station-manager/.env.local`)

```env
# Override API base URL (default: http://localhost:8000/api/v1)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Customer Portal (`web-portals/customer-portal/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Do **not** commit `.env` or `.env.local`. Use `.env.example` in the repo if you want to document variables.

---

## 📋 Development Tips

1. **Always start the backend** before Station Manager or Customer Portal so API calls succeed.
2. **CORS** is set for `http://localhost:3000` and `http://localhost:3001` in `backend/app/main.py`.
3. **Station Manager** uses `@/lib/api` and `@/types`; keep `types/index.ts` in sync with backend Pydantic schemas.
4. **API testing**: Use `http://127.0.0.1:8000/docs` for interactive requests.
5. **Mobile**: Ensure device/emulator can reach `http://10.0.2.2:8000` (Android emulator) or your machine’s IP if testing on a real device.

---

## 👥 Team

| Role | Focus |
|------|--------|
| **Chanul** | Backend, web portals, architecture |
| **Heshadha** | ML, route optimization (see `backend/app/services/optimization.py`) |
| **Nevith** | Mobile app |

---

## 📄 License

This project is part of SDGP CS-155 coursework.
