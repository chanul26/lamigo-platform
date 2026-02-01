# 🚚 LamiGo - Last-Mile Delivery Optimization Platform

LamiGo is a specialized platform designed to optimize last-mile delivery logistics in Sri Lanka. It connects multiple frontends with a FastAPI backend to provide real-time delivery tracking, route optimization, and station management.

**SDGP CS-155 Project**

---

## 🏗️ Architecture Overview

```
lamigo-platform/
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── api/v1/              # API routes (versioned)
│   │   │   └── endpoints/       # packages, drivers, stations
│   │   ├── schemas/             # Pydantic models
│   │   └── services/            # Business logic & ML
│   ├── main.py                  # Legacy entry (imports from app/)
│   └── requirements.txt
│
├── mobile-app/                  # Flutter Driver Application
│   ├── lib/                     # Dart source code
│   ├── android/                 # Android platform files
│   └── pubspec.yaml
│
├── web-portals/                 # Next.js Web Applications
│   ├── station-manager/         # Staff operations portal (port 3000)
│   └── customer-portal/         # Customer tracking portal (port 3001)
│
└── docs/                        # Documentation
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+ / FastAPI |
| **Mobile App** | Flutter / Dart |
| **Web Portals** | Next.js 16 / React 19 / TypeScript |
| **Styling** | Tailwind CSS 4 |
| **ML/AI** | Python (pandas, numpy) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Flutter SDK 3.10+

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

The backend will be running at: **http://127.0.0.1:8000**

- API Documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

### 2. Station Manager Portal (Next.js)

```bash
cd web-portals/station-manager

# Install dependencies
npm install

# Start development server
npm run dev
```

The Station Manager will be running at: **http://localhost:3000**

### 3. Customer Portal (Next.js)

```bash
cd web-portals/customer-portal

# Install dependencies
npm install

# Start development server (different port)
npm run dev -- -p 3001
```

The Customer Portal will be running at: **http://localhost:3001**

### 4. Mobile App (Flutter)

```bash
cd mobile-app

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run
```

---

## 📡 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Backend health check |
| GET | `/api/health` | API health check |

### Packages (`/api/v1/packages`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get all packages |
| GET | `/{id}` | Get package by ID |
| GET | `/tracking/{tracking_number}` | Get package by tracking number |

### Drivers (`/api/v1/drivers`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get all drivers |
| GET | `/active` | Get active drivers only |
| GET | `/{id}` | Get driver by ID |

---

## 🔗 Frontend-Backend Integration

### TypeScript Types

The Station Manager portal includes TypeScript interfaces that mirror the backend Pydantic schemas:

```
web-portals/station-manager/types/index.ts
```

### API Client

A typed API client is available for frontend use:

```typescript
import { apiClient } from '@/lib/api';

// Get all packages
const packages = await apiClient.getPackages();

// Get active drivers
const drivers = await apiClient.getActiveDrivers();
```

---

## 👥 Team Responsibilities

| Member | Focus Area |
|--------|------------|
| **Chanul** | Backend architecture, Web portals |
| **Heshadha** | ML models, Route optimization algorithms |

---

## 🔧 Environment Variables

Create a `.env` file in the respective directories:

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/lamigo
SECRET_KEY=your-secret-key
```

### Web Portals (`web-portals/station-manager/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 📋 Development Workflow

1. **Start Backend First**: Always start the FastAPI server before frontends
2. **Check CORS**: Backend allows `localhost:3000` and `localhost:3001`
3. **API Docs**: Use `/docs` for interactive API testing
4. **Type Safety**: Keep TypeScript interfaces in sync with Pydantic schemas

---

## 🧪 Testing the Integration

1. Start the backend: `uvicorn app.main:app --reload`
2. Start Station Manager: `npm run dev` (in station-manager/)
3. Open http://localhost:3000
4. The dashboard should fetch and display packages/drivers from the API

---

## 📄 License

This project is part of SDGP CS-155 coursework.
