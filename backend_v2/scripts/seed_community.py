"""
scripts/seed_community.py
Seeds 20 community users, 50 product reports, and 100 report images
for PGN Phase 1 testing.

Usage (from backend_v2/):
    python scripts/seed_community.py
"""
import os
import sys
import uuid
import random
from datetime import date, timedelta, datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, Base, engine
from app.community.models.community_user import CommunityUser
from app.community.models.product_report import ProductReport
from app.community.models.report_image   import ReportImage
from app.community.enums import ReportType, Severity, ReportStatus

# ── Seed data ─────────────────────────────────────────────────────────────────

USERS = [
    {"full_name": "Priya Rajan",       "email": "priya.rajan@gmail.com",       "phone": "+919876543210", "country": "India", "state": "Tamil Nadu",    "city": "Chennai"},
    {"full_name": "Arun Kumar",        "email": "arun.kumar@yahoo.com",        "phone": "+919123456780", "country": "India", "state": "Karnataka",     "city": "Bengaluru"},
    {"full_name": "Meena Krishnan",    "email": "meena.k@outlook.com",         "phone": "+919234567891", "country": "India", "state": "Kerala",        "city": "Kochi"},
    {"full_name": "Suresh Pillai",     "email": "suresh.pillai@hotmail.com",   "phone": "+919345678902", "country": "India", "state": "Andhra Pradesh","city": "Hyderabad"},
    {"full_name": "Divya Nair",        "email": "divya.nair@gmail.com",        "phone": "+919456789013", "country": "India", "state": "Tamil Nadu",    "city": "Coimbatore"},
    {"full_name": "Ramesh Iyer",       "email": "ramesh.iyer@gmail.com",       "phone": "+919567890124", "country": "India", "state": "Karnataka",     "city": "Mysuru"},
    {"full_name": "Latha Venkatesh",   "email": "latha.v@protonmail.com",      "phone": "+919678901235", "country": "India", "state": "Tamil Nadu",    "city": "Madurai"},
    {"full_name": "Vijay Shankar",     "email": "vijay.shankar@gmail.com",     "phone": "+919789012346", "country": "India", "state": "Kerala",        "city": "Thiruvananthapuram"},
    {"full_name": "Kavitha Balaji",    "email": "kavitha.b@gmail.com",         "phone": "+919890123457", "country": "India", "state": "Tamil Nadu",    "city": "Salem"},
    {"full_name": "Mohan Das",         "email": "mohan.das@gmail.com",         "phone": "+919901234568", "country": "India", "state": "Karnataka",     "city": "Hubli"},
    {"full_name": "Anitha Reddy",      "email": "anitha.reddy@outlook.com",    "phone": "+918012345679", "country": "India", "state": "Telangana",     "city": "Hyderabad"},
    {"full_name": "Rajesh Murugan",    "email": "rajesh.m@gmail.com",          "phone": "+918123456780", "country": "India", "state": "Tamil Nadu",    "city": "Trichy"},
    {"full_name": "Sunita Joshi",      "email": "sunita.joshi@gmail.com",      "phone": "+918234567891", "country": "India", "state": "Maharashtra",   "city": "Pune"},
    {"full_name": "Deepak Sharma",     "email": "deepak.sharma@gmail.com",     "phone": "+918345678902", "country": "India", "state": "Delhi",         "city": "New Delhi"},
    {"full_name": "Nithya Sundaram",   "email": "nithya.s@gmail.com",          "phone": "+918456789013", "country": "India", "state": "Tamil Nadu",    "city": "Vellore"},
    {"full_name": "Harish Chandar",    "email": "harish.c@yahoo.com",          "phone": "+918567890124", "country": "India", "state": "Karnataka",     "city": "Mangaluru"},
    {"full_name": "Rekha Menon",       "email": "rekha.menon@gmail.com",       "phone": "+918678901235", "country": "India", "state": "Kerala",        "city": "Kozhikode"},
    {"full_name": "Santhosh Kumar",    "email": "santhosh.kumar@gmail.com",    "phone": "+918789012346", "country": "India", "state": "Tamil Nadu",    "city": "Erode"},
    {"full_name": "Pooja Venkataraman","email": "pooja.vr@gmail.com",          "phone": "+918890123457", "country": "India", "state": "Tamil Nadu",    "city": "Tirunelveli"},
    {"full_name": "Bala Subramaniam",  "email": "bala.sub@protonmail.com",     "phone": "+918901234568", "country": "India", "state": "Tamil Nadu",    "city": "Thoothukudi"},
]

BARCODES = [
    "8901030865023", "8906002393053", "8901011043123", "8902102151020",
    "8901491501073", "8901058852093", "8901719114084", "8903522003024",
    "8901764000009", "8902080095027",
]

BATCHES = ["BATCH-A001", "BATCH-B002", "BATCH-C003", "BATCH-D004", "BATCH-E005"]
PRODUCTS = ["Amul Milk 1L", "Parle-G Biscuits", "Maggi Noodles", "Colgate Toothpaste",
            "Vim Dishwash", "Surf Excel 2kg", "Aashirvaad Atta", "Tropicana Orange",
            "MTR Ready-to-eat", "Haldirams Mixture"]
LOCATIONS = ["Zepto - Adyar", "BigBasket Hub", "Blinkit - Velachery", "DMart - Perambur",
             "Swiggy Instamart - OMR", "Fresh To Home", "Spencer's Retail"]
DESCRIPTIONS = [
    "The packaging was clearly dented and the seal was broken when I received it.",
    "The expiry date printed on the packet was smudged and unreadable completely.",
    "There was a very strong and unpleasant smell coming out of the product upon opening.",
    "The bottle was leaking from the bottom when I took it out of the delivery bag.",
    "I ordered the regular variant but received the diet version instead of what I wanted.",
    "Found a small piece of black plastic inside the product which is very concerning.",
    "The hologram on the product appears to be fake and the labeling looks suspicious.",
    "The product color was different from what it normally looks like, seems altered.",
    "The cap was cracked and the liquid had partially evaporated from the bottle already.",
    "Manufacturing date shows a year ago but best before is only 3 months from today.",
]
IMAGE_URLS = [
    "https://cdn.example.com/reports/img_{}.jpg",
    "https://images.pgn.io/evidence/{}.png",
    "https://storage.googleapis.com/pgn-reports/{}.webp",
]

random.seed(42)


def _past_date(days_ago: int) -> date:
    return date.today() - timedelta(days=days_ago)


def seed(db) -> None:
    # ── Users ─────────────────────────────────────────────────────────────────
    created_users = []
    for u in USERS:
        exists = db.query(CommunityUser).filter(CommunityUser.email == u["email"]).first()
        if exists:
            print(f"  SKIP user {u['email']} (already exists)")
            created_users.append(exists)
            continue
        user = CommunityUser(**u, is_verified=random.choice([True, False]))
        db.add(user)
        db.flush()
        created_users.append(user)
        print(f"  INSERT user {u['email']}")

    db.commit()
    print(f"\n  ✔  {len(created_users)} community users ready\n")

    # ── Explicit High-Risk Cluster Seeding ────────────────────────────────────
    created_reports = []
    print("  Seeding high-risk cluster reports...")
    for idx, user in enumerate(created_users[:12]):
        barcode = "8901030499714"
        batch = "BATCH-A001"
        report_type = ReportType.FAKE_PRODUCT
        
        exists = db.query(ProductReport).filter(
            ProductReport.user_id == user.id,
            ProductReport.barcode == barcode,
            ProductReport.batch_number == batch,
            ProductReport.report_type == report_type
        ).first()
        
        if exists:
            created_reports.append(exists)
            continue
            
        report = ProductReport(
            user_id=user.id,
            barcode=barcode,
            batch_number=batch,
            product_name="Amul Milk 1L",
            report_type=report_type,
            severity=Severity.CRITICAL,
            description=f"Explicitly seeded critical report for high-risk cluster testing. (instance #{idx+1})",
            purchase_location="Zepto - Adyar",
            purchase_date=_past_date(random.randint(1, 10)),
            status=ReportStatus.PENDING,
        )
        db.add(report)
        db.flush()
        created_reports.append(report)
        print(f"  INSERT high-risk report #{idx+1} — {barcode} / {report_type.value}")

    db.commit()

    # ── Reports ───────────────────────────────────────────────────────────────
    for i in range(50):
        user        = random.choice(created_users)
        barcode     = random.choice(BARCODES)
        batch       = random.choice(BATCHES)
        report_type = random.choice(list(ReportType))
        severity    = random.choice(list(Severity))
        status      = random.choice(list(ReportStatus))
        description = random.choice(DESCRIPTIONS) + f" (incident #{i+1})"

        # Use unique combination to avoid seeding duplicates on re-run
        exists = (
            db.query(ProductReport)
            .filter(
                ProductReport.user_id     == user.id,
                ProductReport.barcode     == barcode,
                ProductReport.batch_number == batch,
                ProductReport.report_type == report_type,
            )
            .first()
        )
        if exists:
            print(f"  SKIP report #{i+1} (duplicate)")
            created_reports.append(exists)
            continue

        report = ProductReport(
            user_id=user.id,
            barcode=barcode,
            batch_number=batch,
            product_name=random.choice(PRODUCTS),
            report_type=report_type,
            severity=severity,
            description=description,
            purchase_location=random.choice(LOCATIONS),
            purchase_date=_past_date(random.randint(1, 60)),
            status=status,
        )
        db.add(report)
        db.flush()
        created_reports.append(report)
        print(f"  INSERT report #{i+1} — {barcode} / {report_type.value}")

    db.commit()
    print(f"\n  ✔  {len(created_reports)} product reports ready\n")

    # ── Images ────────────────────────────────────────────────────────────────
    image_count = 0
    for i in range(100):
        report = random.choice(created_reports)
        current = db.query(ReportImage).filter(ReportImage.report_id == report.id).count()
        if current >= 5:
            continue
        uid = uuid.uuid4().hex[:8]
        url_template = random.choice(IMAGE_URLS)
        image = ReportImage(
            report_id=report.id,
            image_url=url_template.format(uid),
        )
        db.add(image)
        image_count += 1

    db.commit()
    print(f"  ✔  {image_count} report images ready\n")

    # ── Credibility Records (Seeding Phase 2) ───────────────────────────────
    print("  Seeding report credibility records...")
    from app.community.services.credibility_service import recalculate_report
    
    cred_count = 0
    for r in created_reports:
        recalculate_report(db, r.id)
        cred_count += 1
        
    print(f"  ✔  {cred_count} report credibility records ready\n")

    # ── Issue Clusters (Seeding Phase 3 & 4) ───────────────────────────────
    print("  Seeding PICE issue clusters...")
    from app.community.services.issue_cluster_service import rebuild_all_clusters
    rebuilt_count = rebuild_all_clusters(db)
    print(f"  ✔  {rebuilt_count} reports grouped into issue clusters successfully\n")

    # Count intelligence profiles created
    from app.community.models.cluster_intelligence import ClusterIntelligence
    intel_count = db.query(ClusterIntelligence).count()
    print(f"  ✔  {intel_count} cluster intelligence analytic records compiled successfully\n")

    # Count safety alerts created
    from app.community.models.safety_alert import SafetyAlert
    alert_count = db.query(SafetyAlert).count()
    print(f"  ✔  {alert_count} safety alert records generated based on rules successfully\n")

    # ── Investigation & Case Management (Seeding Phase 6) ──────────────────
    print("  Seeding PGN investigation cases, timeline, evidence, and notes...")
    from app.community.services.investigation_service import create_case, assign_case, add_note, upload_evidence
    
    qualifying_alerts = db.query(SafetyAlert).filter(
        SafetyAlert.alert_level.in_(["HIGH_RISK", "CRITICAL"])
    ).all()
    
    case_count = 0
    for a in qualifying_alerts[:10]:  # Seed up to 10 cases to keep seeding fast
        case = create_case(
            db,
            alert_id=a.id,
            title=f"Investigation: {a.title}",
            description="Seeded investigation triggered automatically due to elevated risk metrics.",
            priority="HIGH" if a.alert_level == "HIGH_RISK" else "CRITICAL"
        )
        assign_case(db, case.id, officer="Officer Rajesh")
        add_note(db, case.id, note_text="Initial safety compliance verification in progress.", created_by="Officer Rajesh")
        upload_evidence(
            db,
            case_id=case.id,
            evidence_type="LAB_REPORT",
            file_url="https://compliance-report.net/verify_batch.pdf",
            description="Official batch contamination audit file.",
            uploaded_by="Officer Rajesh"
        )
        case_count += 1

    from app.community.models.investigation import InvestigationCase
    cases_total = db.query(InvestigationCase).count()
    print(f"  ✔  {cases_total} investigation cases seeded successfully.\n")


if __name__ == "__main__":
    print("\n──────────────────────────────────────────")
    print("  PGN Phase 1 — Community Seed Script")
    print("──────────────────────────────────────────\n")

    db = SessionLocal()
    try:
        seed(db)
        print("──────────────────────────────────────────")
        print("  Seeding complete.")
        print("──────────────────────────────────────────\n")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()
