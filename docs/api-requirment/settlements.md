# API Requirements — Settlements Module

**Frontend Branch:** `pending-api/settlements-ui`  
**Requested by:** Kaarunjan  
**Status:** UI complete, awaiting backend endpoints  

---

## Overview

The Settlements module has two pages:

1. **Settlements Page** (`/settlements`) — lists all drivers with their pending balance, with a Pay button to settle
2. **Payment History Page** (`/settlements/history`) — lists all past payments with filter by driver name and date

---

## Endpoint 1 — Get All Driver Settlements

Used by the main Settlements page to populate the table.

**Method & URL**
```
GET /api/v1/settlements
```

**Expected Response**
```json
[
  {
    "id": 1,
    "driver_id": 1,
    "driver_name": "Saman Kumara",
    "total_pending": 18500
  },
  {
    "id": 2,
    "driver_id": 2,
    "driver_name": "Nimal Perera",
    "total_pending": 4200
  }
]
```

**Notes**
- `total_pending` is the total unpaid amount owed to the driver in LKR
- If `total_pending` is `0`, the Pay button is disabled on the UI — no action needed from backend for those rows
- Driver ID is displayed on the UI as `#DRV-00{driver_id}`

---

## Endpoint 2 — Settle a Payment

Triggered when the station manager confirms a payment in the modal.

**Method & URL**
```
PATCH /api/v1/settlements/{id}/mark-paid
```

**Required Payload**
```json
{
  "payment_method": "cash" | "bank_transfer",
  "amount_paid": 18500
}
```

**Expected Response**
```json
{
  "id": 1,
  "driver_id": 1,
  "driver_name": "Saman Kumara",
  "total_pending": 0
}
```

**Notes**
- After a successful response, the UI resets that driver's `total_pending` to `0` locally
- The payment record should be saved to the database so it appears in the Payment History endpoint below

---

## Endpoint 3 — Get Payment History

Used by the Payment History page (`/settlements/history`).

**Method & URL**
```
GET /api/v1/settlements/history
```

**Query Parameters (optional)**
```
?driver_id={id}     → filter by specific driver
```

**Expected Response**
```json
[
  {
    "id": 1,
    "driver_id": 1,
    "driver_name": "Saman Kumara",
    "amount_paid": 12000,
    "payment_method": "cash",
    "date": "2026-03-01"
  },
  {
    "id": 2,
    "driver_id": 2,
    "driver_name": "Nimal Perera",
    "amount_paid": 8500,
    "payment_method": "bank_transfer",
    "date": "2026-03-03"
  }
]
```

**Notes**
- `date` must be ISO format (`YYYY-MM-DD`) — the UI filters by exact date string match
- `payment_method` must be exactly `"cash"` or `"bank_transfer"` — the UI uses these values to render badge labels and colors
- The UI also filters by driver name client-side, so no server-side name filtering is needed

---

## Data Types Summary

| Field | Type | Notes |
|---|---|---|
| `id` | `int` | Settlement record ID |
| `driver_id` | `int` | Used to display `#DRV-00{driver_id}` |
| `driver_name` | `string` | Full name, used for avatar initials |
| `total_pending` | `int` | Amount in LKR, `0` means nothing to pay |
| `amount_paid` | `int` | Amount in LKR paid in a single settlement |
| `payment_method` | `"cash" \| "bank_transfer"` | Exact string values required |
| `date` | `string` | ISO format `YYYY-MM-DD` |
