# LamiGo — Data Structure Summary (for Mentor)

A high-level overview of the project’s entities, relationships, key fields, and backend tech stack.

---

## 1. Entities (Main Objects)

| Entity | Where defined | Purpose |
|--------|----------------|---------|
| **Organization** | `backend/app/db/models.py` | Tenant (e.g. “CityPack” delivery company). One per organisation. |
| **User** | `backend/app/db/models.py` | Person using the system: linked to Firebase, belongs to one Organisation, has a role. |
| **Package** | `backend/app/schemas/package.py` | A delivery item: tracking number, recipient, address, status. *(API/mock only for now.)* |
| **Driver** | `backend/app/schemas/driver.py` | Delivery driver: name, phone, vehicle type, active flag, optional location. *(API/mock only for now.)* |
| **Station** | `backend/app/schemas/station.py` | Hub/warehouse: name, location code, address, optional coordinates. *(API/mock only for now.)* |

**Note:** Only **Organization** and **User** are persisted in PostgreSQL. **Package**, **Driver**, and **Station** are defined as Pydantic schemas and currently served from in-memory mock data in the API endpoints.

---

## 2. Relationships

- **Organization ↔ User**  
  - One **Organization** has many **Users**.  
  - Each **User** belongs to exactly one **Organization** (`org_id`).

- **Package ↔ Driver** (conceptual, via IDs in schemas)  
  - A **Package** can have an optional `assigned_driver_id`.  
  - So: one **Driver** can have many **Packages**; a **Package** has at most one assigned driver.

- **Package ↔ Station** (conceptual, in schemas)  
  - **PackageCreate** has optional `station_id`.  
  - So: a **Package** can be associated with one **Station**; a **Station** can have many packages (reflected in `package_count` on the Station schema).

There are no foreign keys or ORM relationships yet for Package, Driver, or Station because they are not in the database.

---

## 3. Key Fields (per Entity)

### Organization (DB)
- `id` — Primary key  
- `name` — Organisation name (unique)  
- `created_at` — Creation time  

### User (DB)
- `id` — Primary key  
- `firebase_uid` — Firebase auth UID (unique)  
- `org_id` — FK to Organization  
- `role` — e.g. `SUPER_ADMIN`, `ADMIN`, `STAFF`  
- `email` — User email  
- `created_at` — Creation time  

### Package (Schema / API)
- `id`, `tracking_number`, `recipient_name`, `delivery_address`  
- `status` — `"Pending"` \| `"In Transit"` \| `"Delivered"` \| `"Returned"`  
- `assigned_driver_id` — Optional; links to Driver  
- `station_id` — Optional (in create schema); links to Station  
- `created_at`  

### Driver (Schema / API)
- `id`, `name`, `phone_number`, `vehicle_type` (e.g. Bike, Van, Truck)  
- `is_active` — Used for filtering “active” drivers  
- `current_location_lat`, `current_location_long` — Optional  

### Station (Schema / API)
- `id`, `name`, `location_code` (e.g. COL-01), `address`  
- `latitude`, `longitude` — Optional  
- `is_active`, `package_count`  

---

## 4. Current Tech Stack (Backend)

| Library | Purpose |
|--------|---------|
| **FastAPI** | Web framework, REST API |
| **Uvicorn** | ASGI server |
| **Pydantic** | Request/response validation and schemas (Package, Driver, Station, etc.) |
| **SQLAlchemy** | ORM; used for Organization and User (PostgreSQL) |
| **PostgreSQL** | Database (via `psycopg2-binary`) |
| **Firebase Admin** | Server-side auth (e.g. bootstrap, token verification) |
| **python-dotenv** | Environment config (e.g. `DATABASE_URL`) |
| **python-multipart** | Form/multipart handling |
| **httpx** | HTTP client (e.g. tests) |
| **pandas** / **numpy** | Planned for ML/optimisation (e.g. route optimisation) |

---

## 5. Summary Diagram (Conceptual)

```
Organization (1) ──────────< User (many)
     │
     │  [Future: same org scope for packages/drivers/stations]
     │
Package (many) ── assigned_driver_id ──> Driver (1)
Package (many) ── station_id ──────────> Station (1)
```

This summary reflects the code in `backend/` and `README.md` as of the current scan.
