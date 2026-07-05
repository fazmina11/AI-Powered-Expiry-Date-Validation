# 🛡️ Product Guardian Network (PGN) — Feature Implementation Guide

> **For:** Engineering Teammates  
> **Module:** Community Safety & Product Quality Intelligence  
> **Status:** ✅ Production-Ready & Integrated  
> **Last Updated:** July 2026

---

## 📋 Table of Contents

1. [Feature Overview](#-feature-overview)
2. [System Architecture](#-system-architecture)
3. [Directory Structure](#-directory-structure)
4. [Backend Implementation](#-backend-implementation)
   - [Database Schema](#database-schema)
   - [Core Engines](#core-engines)
   - [API Endpoints Reference](#api-endpoints-reference)
   - [Data Models & Enums](#data-models--enums)
5. [Frontend Implementation](#-frontend-implementation)
   - [Routes & Pages](#routes--pages)
   - [Sidebar Integration](#sidebar-integration)
   - [Layout System](#layout-system)
   - [API Service Pattern](#api-service-pattern)
6. [User Flows](#-user-flows)
   - [Consumer Flow](#consumer-flow-public)
   - [Admin Flow](#admin-flow-dashboard)
7. [Running the Feature Locally](#-running-the-feature-locally)
8. [Database Setup & Seeding](#-database-setup--seeding)
9. [Common Pitfalls & Gotchas](#-common-pitfalls--gotchas)
10. [Environment Variables](#-environment-variables)
11. [Adding New Features](#-adding-new-features)

---

## 🧠 Feature Overview

The **Product Guardian Network (PGN)** is a full-stack consumer safety reporting and intelligence platform built on top of the existing AI expiry validation system.

It enables:

| Who | What |
|---|---|
| **Consumers** | Report defective, expired, fake, or suspicious products via a multi-step public form |
| **QA Admins** | Review incoming reports, assess credibility scores, cluster similar issues, and trigger safety alerts |
| **Safety Officers** | Manage investigation cases, attach evidence, log notes, and resolve or escalate findings |
| **System (Automated)** | Generate AI-driven credibility scores, cluster similar barcode incidents, emit safety alerts, and compute community intelligence profiles |

### Core Modules

```
PGN
├── CRCE — Consumer Report Credibility Engine
├── PICE — Product Issue Clustering Engine  
├── CIE  — Community Intelligence Engine
├── CSAE — Community Safety Alert Engine
└── ICME — Investigation Case Management Engine
```

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                        │
│  localhost:3000                                                   │
│                                                                   │
│  Public Routes:              Admin Routes (uses sidebar):        │
│  /community                  /community/intelligence             │
│  /community/report           /community/reports                  │
│  /community/my-reports       /community/reports/[id]             │
│  /community/my-reports/[id]  /community/clusters                 │
│                              /community/alerts                   │
│                              /community/cases                    │
│                              /community/cases/[id]               │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTP REST (CORS enabled)
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + Uvicorn)                      │
│  localhost:8001                                                   │
│                                                                   │
│  /api/v1/community/users                                         │
│  /api/v1/community/reports          ← CRCE                       │
│  /api/v1/community/credibility      ← CRCE                       │
│  /api/v1/community/clusters         ← PICE                       │
│  /api/v1/community/intelligence     ← CIE                        │
│  /api/v1/community/alerts           ← CSAE                       │
│  /api/v1/community/cases            ← ICME                       │
└────────────────────┬─────────────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                PostgreSQL (schema: community)                     │
│  localhost:5432  DB: expirydb                                    │
│                                                                   │
│  community.community_users          community.issue_clusters     │
│  community.product_reports          community.cluster_reports    │
│  community.report_images            community.cluster_intel      │
│  community.report_credibility       community.safety_alerts      │
│                                     community.investigations     │
│                                     community.case_notes         │
│                                     community.case_evidence      │
│                                     community.case_timeline      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

### Backend (`backend_v2/`)

```
backend_v2/
├── app/
│   ├── community/
│   │   ├── enums.py                    # ReportType, Severity, ReportStatus
│   │   ├── models/
│   │   │   ├── community_user.py       # CommunityUser SQLAlchemy model
│   │   │   ├── product_report.py       # ProductReport + ReportImage
│   │   │   ├── report_credibility.py   # CRCE credibility scores
│   │   │   ├── issue_cluster.py        # IssueCluster + ClusterReport
│   │   │   ├── cluster_intelligence.py # ClusterIntelProfile (CIE)
│   │   │   ├── safety_alert.py         # SafetyAlert model (CSAE)
│   │   │   └── investigation.py        # Investigation + Note + Evidence + Timeline
│   │   ├── schemas/
│   │   │   ├── report_schemas.py
│   │   │   ├── credibility_schemas.py
│   │   │   ├── cluster_schemas.py
│   │   │   ├── intelligence_schemas.py
│   │   │   ├── alert_schemas.py
│   │   │   └── case_schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py             # Router aggregator
│   │   │   ├── user_routes.py
│   │   │   ├── report_routes.py
│   │   │   ├── credibility_routes.py
│   │   │   ├── cluster_routes.py
│   │   │   ├── intelligence_routes.py
│   │   │   ├── alert_routes.py
│   │   │   └── case_routes.py
│   │   └── services/
│   │       ├── credibility_service.py  # CRCE scoring logic
│   │       ├── issue_cluster_service.py # PICE clustering logic
│   │       ├── intelligence_service.py  # CIE computation
│   │       ├── alert_service.py         # CSAE alert generation
│   │       └── case_service.py          # ICME lifecycle logic
│   └── main.py                          # Mounts community router
├── scripts/
│   └── seed_community.py                # Seeds 50 reports + clusters + alerts + case
└── .env                                 # DB connection (use PORT 5432, not 5434)
```

### Frontend (`Frontend/`)

```
Frontend/
├── app/
│   └── community/
│       ├── layout.tsx                   # Conditional sidebar switcher
│       ├── page.tsx                     # Public landing page
│       ├── report/page.tsx              # 4-step consumer report wizard
│       ├── my-reports/
│       │   ├── page.tsx                 # User's report history
│       │   └── [id]/page.tsx            # Report detail + timeline
│       ├── intelligence/page.tsx        # CIE dashboard (admin)
│       ├── reports/
│       │   ├── page.tsx                 # Reports management table (admin)
│       │   └── [id]/page.tsx            # CRCE scorecard & auditor (admin)
│       ├── clusters/page.tsx            # PICE cluster view (admin)
│       ├── alerts/page.tsx              # CSAE safety alerts (admin)
│       └── cases/
│           ├── page.tsx                 # ICME cases list (admin)
│           └── [id]/page.tsx            # Case folder with 4 tabs (admin)
├── components/
│   └── dashboard-sidebar.tsx            # Community Safety section added here
└── services/
    └── apiService.ts                    # apiFetch base utility
```

---

## ⚙️ Backend Implementation

### Database Schema

All PGN tables live in the `community` **PostgreSQL schema** (separate from the main `public` schema), providing namespace isolation.

```sql
-- Auto-created on backend startup via SQLAlchemy
CREATE SCHEMA IF NOT EXISTS community;
```

**Key table relationships:**

```
community_users
    └── product_reports (FK: user_id)
            └── report_images (FK: report_id)
            └── report_credibility (FK: report_id, 1:1)
            └── cluster_reports (FK: report_id, N:1 cluster)

issue_clusters
    └── cluster_reports (FK: cluster_id)
    └── cluster_intelligence (FK: cluster_id, 1:1)
    └── safety_alerts (FK: cluster_id)
    └── investigations (FK: cluster_id)

investigations
    └── case_notes (FK: case_id)
    └── case_evidence (FK: case_id)
    └── case_timeline (FK: case_id, auto-appended)
```

### Core Engines

#### 1. CRCE — Consumer Report Credibility Engine

Calculates a credibility score (0–100) per report based on:
- Has supporting images (+20 pts)
- Barcode format validity (+15 pts)  
- Has purchase location (+15 pts)
- Corroborating reports on same barcode (+25 pts)
- Severity level weighting (+25 pts)

```bash
POST /api/v1/community/credibility/{report_id}/recalculate
```

#### 2. PICE — Product Issue Clustering Engine

Groups reports by `(barcode, report_type)` pairs into `IssueCluster` buckets. Computes risk scores and trend labels: `RAPIDLY_GROWING`, `STABLE`, `DORMANT`.

```bash
POST /api/v1/community/clusters/recalculate
```

#### 3. CIE — Community Intelligence Engine

Generates `ClusterIntelProfile` for each cluster with metrics:
`highest_risk_score`, `fastest_growth_cluster`, `most_active_cluster`, `dormant_clusters`

```bash
POST /api/v1/community/intelligence/recalculate
```

#### 4. CSAE — Community Safety Alert Engine

Monitors cluster risk scores. When risk > 40 and trend is `RAPIDLY_GROWING`, auto-generates an alert with:
- Alert level: `WATCH` | `WARNING` | `CRITICAL`
- Recommended action text
- Affected reports/users/cities count

#### 5. ICME — Investigation Case Management Engine

Full lifecycle case management: `OPEN → ASSIGNED → ACTIVE → RESOLVED → CLOSED`

Every state transition auto-appends a `CaseTimeline` event. Supports notes, evidence uploads, and final decisions.

---

### API Endpoints Reference

**Base URL:** `http://localhost:8001/api/v1`

All responses follow the **envelope format**:
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": { ... }
}
```

> ⚠️ **CRITICAL FOR FRONTEND DEVS:** Always unwrap `.data` from the response.  
> See the [API Service Pattern](#api-service-pattern) section below.

#### Community Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/community/users` | Register a community user |
| `GET` | `/community/users/{id}` | Get user profile |

**Create User:**
```json
{ "full_name": "Ravi Kumar", "email": "ravi@example.com" }
```

---

#### Product Reports (CRCE)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/community/reports` | Submit a new product report |
| `GET` | `/community/reports` | List reports (`?status=PENDING&limit=100`) |
| `GET` | `/community/reports/{id}` | Get single report |
| `PATCH` | `/community/reports/{id}` | Update report status |

**Create Report — Required Fields:**
```json
{
  "user_id": "uuid",               // Must exist in community_users
  "barcode": "8901030865023",
  "batch_number": "BATCH-F100",    // Use "UNKNOWN" if unavailable
  "report_type": "DAMAGED_PACKAGING",
  "severity": "MEDIUM",            // Required! LOW | MEDIUM | HIGH | CRITICAL
  "description": "At least 20 characters describing the problem.",
  "product_name": "Amul Milk 1L",  // Optional
  "purchase_location": "DMart - Chennai Adyar",  // NOTE: NOT "store_name"
  "purchase_date": "2026-07-05",   // ISO date, optional
  "images": [{ "image_url": "https://..." }]  // Optional, max 5
}
```

**Report Types:** `DAMAGED_PACKAGING` | `WRONG_EXPIRY` | `BAD_SMELL` | `LEAKAGE` | `WRONG_PRODUCT` | `FOREIGN_OBJECT` | `FAKE_PRODUCT` | `OTHER`

**Report Status:** `PENDING` → `UNDER_REVIEW` → `VERIFIED` | `REJECTED`

---

#### Credibility (CRCE)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/community/credibility/{report_id}` | Get credibility scorecard |
| `POST` | `/community/credibility/{report_id}/recalculate` | Force recalculation |

---

#### Issue Clusters (PICE)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/community/clusters` | List all clusters |
| `GET` | `/community/clusters/{id}` | Cluster detail |
| `GET` | `/community/clusters/{id}/reports` | Reports within a cluster |
| `POST` | `/community/clusters/recalculate` | Rebuild all clusters |

---

#### Community Intelligence (CIE)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/community/intelligence` | All intelligence profiles |
| `GET` | `/community/intelligence/dashboard` | Dashboard summary |
| `GET` | `/community/intelligence/high-risk` | High-risk clusters |
| `GET` | `/community/intelligence/trending` | Trending clusters |
| `GET` | `/community/intelligence/dormant` | Dormant clusters |
| `POST` | `/community/intelligence/recalculate` | Force CIE recompute |

---

#### Safety Alerts (CSAE)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/community/alerts` | List alerts (`?status=ACTIVE&limit=100`) |
| `GET` | `/community/alerts/{id}` | Alert detail |
| `PATCH` | `/community/alerts/{id}/acknowledge` | Acknowledge alert |
| `PATCH` | `/community/alerts/{id}/resolve` | Resolve (`?remarks=text`) |
| `POST` | `/community/alerts/{id}/launch-case` | Spawn investigation case |

**Launch Case Body:**
```json
{
  "title": "Investigation: FAKE_PRODUCT on barcode 8901030499714",
  "description": "Multiple consumers reported this product as counterfeit.",
  "priority": "CRITICAL"
}
```

---

#### Investigation Cases (ICME)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/community/cases` | List all cases |
| `GET` | `/community/cases/{id}` | Full case folder (notes, evidence, timeline embedded) |
| `PATCH` | `/community/cases/{id}/assign` | Assign officer (`?officer=Name`) |
| `PATCH` | `/community/cases/{id}/status` | Update status (`?status=ACTIVE&remarks=...`) |
| `PATCH` | `/community/cases/{id}/resolve` | Resolve (`?resolution=text&final_decision=RECOMMEND_RECALL`) |
| `PATCH` | `/community/cases/{id}/close` | Archive and close |
| `POST` | `/community/cases/{id}/notes` | Add note |
| `POST` | `/community/cases/{id}/evidence` | Upload evidence reference |

**Add Note:**
```json
{ "note": "Lab samples collected from batch F100.", "created_by": "Officer Priya" }
```

**Attach Evidence:**
```json
{
  "evidence_type": "LAB_REPORT",
  "file_url": "https://compliance.net/report.pdf",
  "description": "Chemical assay confirming contamination",
  "uploaded_by": "Officer Priya"
}
```

**Final Decision Values:** `RECOMMEND_RECALL` | `CONTINUE_MONITORING` | `NO_ACTION_REQUIRED` | `SEND_SUPPLIER_WARNING`

**Case Status Values:** `OPEN` → `ASSIGNED` → `ACTIVE` → `UNDER_REVIEW` → `PENDING_EVIDENCE` → `ACTION_TAKEN` → `RESOLVED` → `CLOSED`

> 📖 **Full interactive API docs:** `http://localhost:8001/docs`

---

### Data Models & Enums

```python
# backend_v2/app/community/enums.py

class ReportType(str, Enum):
    DAMAGED_PACKAGING = "DAMAGED_PACKAGING"
    WRONG_EXPIRY      = "WRONG_EXPIRY"
    BAD_SMELL         = "BAD_SMELL"
    LEAKAGE           = "LEAKAGE"
    WRONG_PRODUCT     = "WRONG_PRODUCT"
    FOREIGN_OBJECT    = "FOREIGN_OBJECT"
    FAKE_PRODUCT      = "FAKE_PRODUCT"
    OTHER             = "OTHER"

class Severity(str, Enum):
    LOW, MEDIUM, HIGH, CRITICAL

class ReportStatus(str, Enum):
    PENDING, UNDER_REVIEW, VERIFIED, REJECTED
```

---

## 🖥️ Frontend Implementation

### Routes & Pages

| Route | Access | Description |
|-------|--------|-------------|
| `/community` | Public | Landing page with stats and CTA |
| `/community/report` | Public | 4-step report wizard |
| `/community/my-reports` | Public | User's submitted reports (localStorage-tracked) |
| `/community/my-reports/[id]` | Public | Report detail + timeline |
| `/community/intelligence` | Admin | CIE metrics dashboard |
| `/community/reports` | Admin | Reports management table with status tabs |
| `/community/reports/[id]` | Admin | CRCE scorecard + audit actions |
| `/community/clusters` | Admin | PICE cluster view + reports modal |
| `/community/alerts` | Admin | CSAE safety alerts + acknowledge/resolve/launch |
| `/community/cases` | Admin | ICME investigation cases table |
| `/community/cases/[id]` | Admin | Full case folder with 4 tabs + operations panel |

### Sidebar Integration

The `"Community Safety"` section was added to the **existing** `DashboardSidebar`:

```tsx
// Frontend/components/dashboard-sidebar.tsx

const communitySafetyItems = [
  { label: "Dashboard",              href: "/dashboard/community-safety", icon: LayoutDashboard },
  { label: "Community Reports",      href: "/community/reports",          icon: FileText },
  { label: "Issue Clusters",         href: "/community/clusters",         icon: Layers },
  { label: "Community Intelligence", href: "/community/intelligence",     icon: Brain },
  { label: "Safety Alerts",          href: "/community/alerts",           icon: ShieldAlert },
  { label: "Investigation Cases",    href: "/community/cases",            icon: FolderKanban },
];
```

### Layout System

`app/community/layout.tsx` uses a **pathname-based conditional layout** — no new layout files or directories needed:

```tsx
// app/community/layout.tsx

"use client";
import { usePathname } from "next/navigation";
import DashboardSidebar from "@/components/dashboard-sidebar";

// These paths get the admin sidebar wrapper
const ADMIN_PATHS = [
  "/community/reports",
  "/community/clusters",
  "/community/intelligence",
  "/community/alerts",
  "/community/cases",
];

export default function CommunityLayout({ children }) {
  const pathname = usePathname();
  const isAdminPath = ADMIN_PATHS.some(p => pathname.startsWith(p));

  if (isAdminPath) {
    return (
      <div className="flex min-h-screen">
        <DashboardSidebar />
        <main className="flex-1 ml-64 bg-white">{children}</main>
      </div>
    );
  }

  // Public routes render under the gradient/nav wrapper
  return <div className="community-public-wrapper">{children}</div>;
}
```

> 💡 **When adding a new admin route** under `/community/*`, add it to `ADMIN_PATHS` in this file.

### API Service Pattern

All community pages use the shared `apiFetch` from `services/apiService.ts`.

```typescript
import { apiFetch } from "@/services/apiService";

// ─── Pattern 1: Fetch a list ──────────────────────────────────────────
const res = await apiFetch<{ data: MyType[] }>("/community/reports?limit=100");
const list = Array.isArray(res) ? res : (res.data || []);

// ─── Pattern 2: Fetch a single object ────────────────────────────────
const raw = await apiFetch<any>(`/community/cases/${id}`);
const item: InvestigationCase = raw?.data || raw;

// ─── Pattern 3: Mutations (POST / PATCH) ─────────────────────────────
const raw = await apiFetch<any>(`/community/cases/${id}/assign?officer=Priya`, {
  method: "PATCH"
});
const updated: InvestigationCase = raw?.data || raw;

// ─── Pattern 4: Create community user (for report submission) ─────────
let userId = localStorage.getItem("community_user_id");
if (!userId) {
  const userRaw = await apiFetch<any>("/community/users", {
    method: "POST",
    body: JSON.stringify({ full_name: "Reporter", email: `guest-${Date.now()}@pgn.community` }),
  });
  userId = userRaw?.data?.id || userRaw.id;
  localStorage.setItem("community_user_id", userId);
}

// ─── Pattern 5: Seeded image URLs need host prefix ───────────────────
const getImageUrl = (url: string) =>
  url.startsWith("http") ? url : `http://localhost:8001${url}`;
```

---

## 🔄 User Flows

### Consumer Flow (Public)

```
Consumer visits /community
  │
  ▼  Click "+ Report Product"
/community/report
  │
  Step 1: Product Info
    - Product Name (required)
    - Barcode / SKU (required)
    - Batch Number, Purchase Date, Store Name, Store Location (optional)
  │
  Step 2: Issue Details
    - Issue Type (required, 1 of 8 types)
    - Description (required, min 20 chars)
  │
  Step 3: Evidence
    - Upload up to 5 photos (optional, recommended)
  │
  Step 4: Review & Submit
    POST /api/v1/community/reports
    - Auto-creates guest user if needed (localStorage cached)
    - Stores report ID in localStorage["my_report_ids"]
  │
  ▼  Success Screen → Click "View My Reports"
/community/my-reports
  - Filtered by localStorage["my_report_ids"]
  │
  ▼  Click "View Details"
/community/my-reports/[id]
  - Report metadata, status progress bar, image gallery, timeline
```

### Admin Flow (Dashboard)

```
Admin (Sidebar → Community Safety)
  │
  ├─▶ /community/intelligence
  │     View CIE profiles per cluster
  │     Filter: All / High-Risk / Trending / Dormant
  │     Click "Force CIE Recalculation"
  │
  ├─▶ /community/reports
  │     Filter by status tabs: PENDING / UNDER_REVIEW / VERIFIED / REJECTED
  │     Search by barcode, product name
  │     Click "Inspect" →
  │         /community/reports/[id]
  │             - CRCE credibility scorecard (circular gauge + rules checklist)
  │             - Recalculate credibility score
  │             - Update report status
  │
  ├─▶ /community/clusters
  │     View all PICE issue clusters
  │     Risk score + report count per cluster
  │     Click "Reports Group" → modal with all grouped reports
  │     Click "Rebuild Issue Clusters"
  │
  ├─▶ /community/alerts
  │     Severity cards: CRITICAL / WARNING / WATCH / ACTIVE count
  │     Per alert: Acknowledge | Resolve (with remarks) | Launch Case
  │
  └─▶ /community/cases
        Table: Case Number | Title | Priority | Status | Officer | Date
        Status badge colors: ASSIGNED=violet | RESOLVED=green | CLOSED=slate
        Click "Inspect Folder" →
            /community/cases/[id]
                ┌─ Tab: Case Folder Info ─┐
                │  Case number, officer,   │
                │  dates, mission brief,   │
                │  resolution summary      │
                └─────────────────────────┘
                ┌─ Tab: Investigative Notes ─┐
                │  Timeline of notes         │
                │  Add new note + created_by │
                └────────────────────────────┘
                ┌─ Tab: Evidence Attachments ─┐
                │  Grid of file references    │
                │  Attach new evidence URL    │
                └─────────────────────────────┘
                ┌─ Tab: Timeline Audit Log ─┐
                │  Auto-chronological events │
                │  event_type + description  │
                │  + performed_by + date     │
                └────────────────────────────┘
                
                Right Panel: Case Operations Panel
                  [Assign Officer]  → PATCH /cases/{id}/assign
                  [Update Status]   → PATCH /cases/{id}/status
                  [Mark Resolved]   → PATCH /cases/{id}/resolve
                  [Archive & Close] → PATCH /cases/{id}/close
```

---

## 🚀 Running the Feature Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ on `localhost:5432`
- Database: `expirydb`

### Step 1 — Start the Backend

```powershell
# Navigate to backend directory
cd e:\AI-Powered-Expiry-Date-Validation\backend_v2

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Verify it is healthy
curl http://localhost:8001/health
# Expected: {"status":"healthy","database":"connected"}
```

### Step 2 — Start the Frontend

```powershell
# Navigate to frontend directory
cd e:\AI-Powered-Expiry-Date-Validation\Frontend

# Install Node dependencies (first time only)
npm install

# Start dev server
npm run dev

# Open in browser
# → http://localhost:3000/community       (Public landing)
# → http://localhost:3000/community/cases (Admin cases)
```

### Step 3 — Verify Integration

| URL | Expected Result |
|-----|----------------|
| `http://localhost:8001/health` | `{"status":"healthy","database":"connected"}` |
| `http://localhost:8001/docs` | Swagger UI with all community endpoints |
| `http://localhost:3000/community` | Public PGN landing page |
| `http://localhost:3000/community/intelligence` | CIE admin dashboard |
| `http://localhost:3000/community/reports` | Reports management table |
| `http://localhost:3000/community/cases` | Investigation cases list |

---

## 🗄️ Database Setup & Seeding

### First-Time Setup

The community schema is **auto-created** on backend startup via SQLAlchemy. No manual migrations required.

If tables are in a broken/conflicting state:

```sql
-- In psql connected to expirydb
DROP SCHEMA community CASCADE;
CREATE SCHEMA community;
-- Then restart the backend — it will recreate all tables automatically
```

### Seeding Sample Data

```powershell
cd e:\AI-Powered-Expiry-Date-Validation\backend_v2

# Set UTF-8 encoding (Windows)
$env:PYTHONIOENCODING='utf-8'

# Run seed script
python scripts/seed_community.py
```

**What gets seeded:**
- ~10 community users
- ~50 product reports with images
- ~50 credibility scores
- ~51 issue clusters
- ~51 safety alerts
- 1 investigation case with notes, evidence, and 4 timeline events

### Data Counts After Seeding

| Table | Count |
|-------|-------|
| `community_users` | ~10 |
| `product_reports` | ~50 |
| `report_credibility` | ~50 |
| `issue_clusters` | ~51 |
| `safety_alerts` | ~51 |
| `investigations` | 1 |
| `case_timeline` | 4 |

---

## ⚠️ Common Pitfalls & Gotchas

### 1. ❌ Forgetting to Unwrap `.data`

The **most common bug** — every community endpoint returns a wrapper envelope:

```typescript
// ❌ WRONG — res is { success: true, message: "...", data: [...] }
const cases = await apiFetch<InvestigationCase[]>("/community/cases");
cases.map(...) // TypeError: cases.map is not a function

// ✅ CORRECT
const res = await apiFetch<{ data: InvestigationCase[] }>("/community/cases");
const cases = Array.isArray(res) ? res : (res.data || []);
```

### 2. ❌ Wrong Field Name in Report Submission

```typescript
// ❌ WRONG — backend schema does NOT have store_name or store_location
{
  store_name: "DMart",
  store_location: "Chennai"
}

// ✅ CORRECT — combine into purchase_location
{
  purchase_location: "DMart - Chennai",  // single field
  severity: "MEDIUM"                      // required, often forgotten
}
```

### 3. ❌ Wrong Timeline Field Names

The case timeline uses different field names than you might expect:

```typescript
// ❌ WRONG
event.description  // undefined
event.created_by   // undefined

// ✅ CORRECT (from actual backend response)
event.event_description  // "Case assigned to Officer Priya."
event.performed_by       // "Officer Priya"
```

### 4. ❌ Wrong Database Port

```env
# ❌ WRONG — Docker container mapped port, not local service
DATABASE_URL=postgresql://postgres:pass@127.0.0.1:5434/expirydb

# ✅ CORRECT — actual local PostgreSQL port
DATABASE_URL=postgresql://postgres:pass@127.0.0.1:5432/expirydb
```

### 5. ❌ Missing ASSIGNED Status in UI

The backend case status lifecycle includes `ASSIGNED` which the frontend must handle:

```typescript
// ✅ Add ASSIGNED to status badge logic
c.status === "RESOLVED" ? "text-green-700 bg-green-50 border-green-200" :
c.status === "CLOSED"   ? "text-slate-700 bg-slate-50 border-slate-200" :
c.status === "ASSIGNED" ? "text-violet-700 bg-violet-50 border-violet-200" :
                          "text-amber-700 bg-amber-50 border-amber-200"
```

### 6. ❌ New Admin Routes Not Getting Sidebar

When adding a new admin route, update `ADMIN_PATHS` in `app/community/layout.tsx`:

```typescript
const ADMIN_PATHS = [
  "/community/reports",
  "/community/clusters",
  "/community/intelligence",
  "/community/alerts",
  "/community/cases",
  "/community/your-new-module",  // ← Add here
];
```

---

## 🔐 Environment Variables

### Backend (`backend_v2/.env`)

```env
DATABASE_URL=postgresql://postgres:your_password@127.0.0.1:5432/expirydb
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Frontend (`Frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
```

---

## 🔧 Adding New Features

### Adding a New Admin Page

```bash
# 1. Create the page
Frontend/app/community/my-module/page.tsx

# 2. Add to sidebar (components/dashboard-sidebar.tsx)
{ label: "My Module", href: "/community/my-module", icon: SomeIcon }

# 3. Add to ADMIN_PATHS (app/community/layout.tsx)
"/community/my-module"

# 4. Fetch data with unwrap pattern
const res = await apiFetch<{ data: MyType[] }>("/community/my-endpoint");
const data = Array.isArray(res) ? res : (res.data || []);
```

### Adding a New Backend Route

```python
# 1. Create schema: app/community/schemas/my_schema.py
# 2. Create route: app/community/routes/my_routes.py

from fastapi import APIRouter
router = APIRouter()

@router.get("/", response_model=ApiResponse[List[MySchema]])
def list_my_items(db: Session = Depends(get_db)):
    items = db.query(MyModel).all()
    return success_response(items)

# 3. Register in app/community/routes/__init__.py
from .my_routes import router as my_router
router.include_router(my_router, prefix="/my-module", tags=["My Module"])

# The community router is already mounted in app/main.py at /api/v1/community
# so your endpoint will be at: /api/v1/community/my-module
```

---

## 🧪 Quick Smoke Test

Run these to verify the full stack:

```bash
# Health check
curl http://localhost:8001/health

# List reports (expect array with 50+ items)
curl http://localhost:8001/api/v1/community/reports?limit=5

# List alerts
curl http://localhost:8001/api/v1/community/alerts?limit=3

# List cases
curl http://localhost:8001/api/v1/community/cases

# Submit a test report
curl -X POST http://localhost:8001/api/v1/community/reports \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "6b684913-2a6b-4f1a-8864-f976ed2f551b",
    "barcode": "8901030865023",
    "batch_number": "BATCH-TEST",
    "product_name": "Test Product",
    "report_type": "DAMAGED_PACKAGING",
    "severity": "MEDIUM",
    "description": "This is a test submission - at least 20 chars for validation to pass."
  }'
```

---

## 📌 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Separate `community` PostgreSQL schema | Isolates PGN data from core inventory tables; easier to wipe/migrate independently |
| Response envelope `{ success, message, data }` | Consistent structured responses across all endpoints; frontend must always unwrap `.data` |
| Guest user via localStorage | Avoids requiring consumer login to submit reports; ID persists across browser sessions |
| Pathname-based layout switch in `layout.tsx` | Reuses existing dashboard sidebar without duplicating layout trees or nested directories |
| Notes/Evidence/Timeline embedded in `GET /cases/{id}` | Single API call for case folder view; reduces round-trips on detail page load |
| Auto-appended timeline on every state change | Full audit trail without developers manually creating timeline entries |
| `seed_community.py` script | Realistic demo data for team development without requiring a production environment |

---

*Part of the AI-Powered Expiry Date Validation Platform*  
*Product Guardian Network (PGN) — Phase 1 Implementation*

*For backend questions: refer to `backend_v2/app/community/`*  
*For frontend questions: refer to `Frontend/app/community/`*  
*Interactive API docs: `http://localhost:8001/docs`*
