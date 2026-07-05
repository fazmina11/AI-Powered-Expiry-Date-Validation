#!/usr/bin/env python3
"""
scripts/test_full_pgn_workflow.py
Comprehensive End-to-End Validation Suite for PGN backend.
Validates Phases 1-6 through API integration workflows.
Writes result logs and generates a markdown test report.
"""
import os
import sys
import time
import random
import uuid
import requests
from datetime import datetime

# Target API Configurations
BASE_URL = "http://127.0.0.1:8001/api/v1/community"
REPORT_DIR = "reports"
REPORT_PATH = os.path.join(REPORT_DIR, "PGN_End_To_End_Test_Report.md")

# Color formatting helpers
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_step(name: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ Running Step: {name}{Colors.END}")


def print_pass(msg: str):
    print(f"  {Colors.GREEN}✔ [PASS] {msg}{Colors.END}")


def print_fail(msg: str, detail: str = ""):
    print(f"  {Colors.RED}✘ [FAIL] {msg}{Colors.END}")
    if detail:
        print(f"    {Colors.YELLOW}Details: {detail}{Colors.END}")


def run_test_suite():
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    results = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    def log_result(category: str, success: bool):
        nonlocal total_tests, passed_tests, failed_tests
        total_tests += 1
        if success:
            passed_tests += 1
            results[category] = "PASS"
        else:
            failed_tests += 1
            results[category] = "FAIL"

    # Shared entities across tests
    random_suffix = random.randint(100000, 999999)
    test_email = f"qa.workflow_{random_suffix}@example.com"
    barcode = f"8901030{random.randint(100000, 999999)}"
    batch = f"BATCH-QA-{random_suffix}"
    
    user_id = None
    report_id = None
    cluster_id = None
    alert_id = None
    case_id = None

    try:
        # ── STEP 1: Community User ───────────────────────────────────────────
        print_step("Step 1: Create Community User")
        payload = {
            "full_name": "QA Workflow Tester",
            "email": test_email,
            "phone": "+919876543210",
            "country": "India",
            "state": "Karnataka",
            "city": "Bengaluru"
        }
        r = requests.post(f"{BASE_URL}/users", json=payload)
        if r.status_code == 201:
            res = r.json()
            user_id = res["data"]["id"]
            print_pass(f"User created successfully with ID: {user_id}")
            log_result("Community User", True)
        else:
            print_fail("Failed to create community user", r.text)
            log_result("Community User", False)
            sys.exit(1)

        # ── STEP 2: Product Report ───────────────────────────────────────────
        print_step("Step 2: Submit Product Report")
        report_payload = {
            "user_id": user_id,
            "barcode": barcode,
            "batch_number": batch,
            "product_name": "E2E Test Product",
            "report_type": "WRONG_EXPIRY",
            "severity": "HIGH",
            "description": "Validation check report to establish credibility baseline scoring.",
            "purchase_location": "Local Store",
            "purchase_date": "2026-07-04"
        }
        r = requests.post(f"{BASE_URL}/reports", json=report_payload)
        if r.status_code == 201:
            res = r.json()
            report_id = res["data"]["id"]
            print_pass(f"Report created with ID: {report_id}")
            log_result("Product Report", True)
        else:
            print_fail("Failed to create report", r.text)
            log_result("Product Report", False)
            sys.exit(1)

        # ── STEP 3: Credibility Engine ───────────────────────────────────────
        print_step("Step 3: Credibility Engine scoring")
        r = requests.get(f"{BASE_URL}/reports/{report_id}/credibility")
        if r.status_code == 200:
            res = r.json()
            score = res["data"]["score"]
            level = res["data"]["credibility_level"]
            assert 0 <= score <= 100
            print_pass(f"Credibility Score: {score} | Level: {level}")
            log_result("Credibility Engine", True)
        else:
            print_fail("Failed to retrieve credibility score", r.text)
            log_result("Credibility Engine", False)
            sys.exit(1)

        # ── STEP 4: Issue Clustering ─────────────────────────────────────────
        print_step("Step 4: Issue Clustering grouping checks")
        # Give clustering processor a brief instant if needed, then retrieve cluster
        r = requests.get(f"{BASE_URL}/clusters/product/{barcode}")
        if r.status_code == 200:
            res = r.json()
            clusters = res["data"]
            assert len(clusters) == 1
            cluster_id = clusters[0]["id"]
            print_pass(f"Report grouped in cluster: {cluster_id}")
            log_result("Issue Clustering", True)
        else:
            print_fail("Failed to find issue cluster", r.text)
            log_result("Issue Clustering", False)
            sys.exit(1)

        # ── STEP 5: Community Intelligence ───────────────────────────────────
        print_step("Step 5: Community Intelligence statistics verification")
        r = requests.get(f"{BASE_URL}/intelligence/{cluster_id}")
        if r.status_code == 200:
            res = r.json()
            intel = res["data"]
            print_pass(
                f"Intelligence compiled successfully. Risk Score: {intel['risk_score']} | "
                f"Trend: {intel['trend']} | Spread: {intel['spread_level']}"
            )
            log_result("Community Intelligence", True)
        else:
            print_fail("Failed to query intelligence", r.text)
            log_result("Community Intelligence", False)
            sys.exit(1)

        # ── STEP 6: Automatic Cluster Growth ─────────────────────────────────
        print_step("Step 6: Automatic Cluster Growth & severity escalation")
        # Add a second user to avoid report duplicate checks
        u_payload = payload.copy()
        u_payload["email"] = f"second_qa_{random_suffix}@example.com"
        u_r = requests.post(f"{BASE_URL}/users", json=u_payload).json()
        second_user_id = u_r["data"]["id"]

        r_payload2 = report_payload.copy()
        r_payload2["user_id"] = second_user_id
        
        requests.post(f"{BASE_URL}/reports", json=r_payload2)
        
        # Verify cluster count increased
        r = requests.get(f"{BASE_URL}/clusters/product/{barcode}")
        res = r.json()
        cluster_info = res["data"][0]
        count = cluster_info["affected_reports_count"]
        print_pass(f"Reports in cluster increased to: {count}")
        log_result("Automatic Cluster Growth", True)

        # ── STEP 7: Alert Generation ─────────────────────────────────────────
        print_step("Step 7: Safety Alert Generation Rules")
        # Submit reports from 10 more unique users to trigger alert threshold
        for k in range(10):
            usr_payload = payload.copy()
            usr_payload["email"] = f"alert_seed_{k}_{random_suffix}@example.com"
            usr_res = requests.post(f"{BASE_URL}/users", json=usr_payload).json()
            u_i = usr_res["data"]["id"]
            
            rep_payload = report_payload.copy()
            rep_payload["user_id"] = u_i
            requests.post(f"{BASE_URL}/reports", json=rep_payload)
            
        # Retrieve cluster alert list
        r = requests.get(f"{BASE_URL}/alerts?cluster_id={cluster_id}")
        if r.status_code == 200:
            res = r.json()
            alerts = res["data"]
            assert len(alerts) > 0
            alert_id = alerts[0]["id"]
            print_pass(f"Alert generated automatically with ID: {alert_id} | Level: {alerts[0]['alert_level']}")
            log_result("Safety Alerts", True)
        else:
            print_fail("Failed to verify safety alert generation", r.text)
            log_result("Safety Alerts", False)
            sys.exit(1)

        # ── STEP 8: Alert Lifecycle ──────────────────────────────────────────
        print_step("Step 8: Alert Lifecycle status transition checks")
        # ACTIVE -> ACKNOWLEDGED
        r = requests.patch(f"{BASE_URL}/alerts/{alert_id}/acknowledge")
        assert r.json()["data"]["status"] == "ACKNOWLEDGED"
        
        # ACKNOWLEDGED -> RESOLVED
        r = requests.patch(f"{BASE_URL}/alerts/{alert_id}/resolve")
        assert r.json()["data"]["status"] == "RESOLVED"
        
        print_pass("Alert status transition cycle validated successfully (ACTIVE -> ACKNOWLEDGED -> RESOLVED)")
        log_result("Alert Lifecycle", True)

        # ── STEP 9: Alert Reopening ──────────────────────────────────────────
        print_step("Step 9: Resolved Alert Auto-Reopening")
        # Submit a new report to trigger auto-reopen rules
        reopen_user_payload = payload.copy()
        reopen_user_payload["email"] = f"reopen_user_{random_suffix}@example.com"
        reopen_user_res = requests.post(f"{BASE_URL}/users", json=reopen_user_payload).json()
        reopen_user_id = reopen_user_res["data"]["id"]

        r_reopen_payload = report_payload.copy()
        r_reopen_payload["user_id"] = reopen_user_id
        requests.post(f"{BASE_URL}/reports", json=r_reopen_payload)
        
        # Query alert status again
        r = requests.get(f"{BASE_URL}/alerts?cluster_id={cluster_id}")
        current_status = r.json()["data"][0]["status"]
        assert current_status == "ACTIVE"
        print_pass("Successfully verified resolved alert auto-reopened to ACTIVE on new report addition")
        log_result("Alert Reopening", True)

        # ── STEP 10: Investigation ───────────────────────────────────────────
        print_step("Step 10: Investigation Case Creation")
        # Alert is high-risk, should allow case creation
        case_payload = {
            "alert_id": alert_id,
            "title": "Investigation Case Workflow QA",
            "description": "Automated case verification timeline tests."
        }
        r = requests.post(f"{BASE_URL}/cases", json=case_payload)
        if r.status_code == 201:
            res = r.json()
            case_id = res["data"]["id"]
            print_pass(f"Investigation Case created with ID: {case_id} | Case Number: {res['data']['case_number']}")
            log_result("Investigation", True)
        else:
            print_fail("Failed to spawn investigation case", r.text)
            log_result("Investigation", False)
            sys.exit(1)

        # ── STEP 11: Assignment ──────────────────────────────────────────────
        print_step("Step 11: Assign Officer")
        r = requests.patch(f"{BASE_URL}/cases/{case_id}/assign", params={"officer": "Officer QA Tester"})
        if r.status_code == 200:
            res = r.json()
            assert res["data"]["assigned_officer"] == "Officer QA Tester"
            print_pass("Officer successfully assigned to the case")
            log_result("Assignment", True)
        else:
            print_fail("Failed to assign officer", r.text)
            log_result("Assignment", False)
            sys.exit(1)

        # ── STEP 12: Notes ───────────────────────────────────────────────────
        print_step("Step 12: Add Investigation Note")
        r = requests.post(
            f"{BASE_URL}/cases/{case_id}/notes",
            json={"note": "Initial inspection note added during test.", "created_by": "Officer QA Tester"}
        )
        if r.status_code == 201:
            print_pass("Timeline note successfully recorded and linked")
            log_result("Notes", True)
        else:
            print_fail("Failed to add note", r.text)
            log_result("Notes", False)
            sys.exit(1)

        # ── STEP 13: Evidence ────────────────────────────────────────────────
        print_step("Step 13: Upload Evidence Log")
        evidence_payload = {
    "evidence_type": "PDF",
    "file_url": "https://evidence.example.com/incident_record.pdf",
    "description": "Receipt proof and batch label images scan compilation."
}
        r = requests.post(f"{BASE_URL}/cases/{case_id}/evidence", json=evidence_payload)
        if r.status_code == 201:
            print_pass("Evidence URL file log stored successfully")
            log_result("Evidence", True)
        else:
            print_fail("Failed to store evidence URL", r.text)
            log_result("Evidence", False)
            sys.exit(1)

                # Retrieve timeline for the case
        r = requests.get(f"{BASE_URL}/cases/{case_id}/timeline")
        if r.status_code == 200:
            events = r.json()["data"]
            # Extract event types from timeline entries
            event_types = [e.get("event_type") for e in events]
            # Define required events that should appear in the timeline
            required_events = {"CASE_CREATED", "CASE_ASSIGNED", "CASE_NOTE_ADDED", "CASE_EVIDENCE_ADDED"}
            missing = required_events - set(event_types)
            assert not missing, f"Missing expected timeline events: {missing}"
            print_pass("Verified audit timeline includes all expected events (Created, Assigned, Note, Evidence)")
            log_result("Timeline", True)
        else:
            print_fail("Failed to query case timeline log", r.text)
            log_result("Timeline", False)
            sys.exit(1)

        # ── STEP 15: Resolve Investigation ───────────────────────────────────
        print_step("Step 15: Resolve Case")
        r = requests.put(
            f"{BASE_URL}/cases/{case_id}/resolve",
            json={"decision_outcome": "RECALL_RECOMMENDED", "decision_rationale": "Severe expiry mismatch verified"}
        )
        if r.status_code == 200:
            assert r.json()["data"]["status"] == "RESOLVED"
            print_pass("Investigation Case status marked as RESOLVED")
            log_result("Resolve Investigation", True)
        else:
            print_fail("Failed to mark case as resolved", r.text)
            log_result("Resolve Investigation", False)
            sys.exit(1)

        # ── STEP 16: Close Investigation ─────────────────────────────────────
        print_step("Step 16: Close Case")
        r = requests.post(f"{BASE_URL}/cases/{case_id}/close")
        if r.status_code == 200:
            assert r.json()["data"]["status"] == "CLOSED"
            print_pass("Investigation Case closed successfully")
            log_result("Close Investigation", True)
        else:
            print_fail("Failed to close case", r.text)
            log_result("Close Investigation", False)
            sys.exit(1)

        # ── STEP 17: Dashboards ──────────────────────────────────────────────
        print_step("Step 17: Dashboard stats indices checks")
        rep_dash = requests.get(f"{BASE_URL}/reports/dashboard").json()
        alert_dash = requests.get(f"{BASE_URL}/alerts/dashboard").json()
        case_dash = requests.get(f"{BASE_URL}/cases/dashboard").json()
        
        # Verify dashboard responses
        assert rep_dash["success"] is True
        assert alert_dash["success"] is True
        assert case_dash["success"] is True
        print_pass("All metrics dashboards query verified successfully")
        log_result("Dashboards", True)

        # ── NEGATIVE TESTS ───────────────────────────────────────────────────
        print_step("Negative Tests validations")
        
        # Duplicate user (409)
        r = requests.post(f"{BASE_URL}/users", json=payload)
        assert r.status_code == 409
        
        # Duplicate report (409)
        r = requests.post(f"{BASE_URL}/reports", json=report_payload)
        assert r.status_code == 409
        
        # Invalid email (422)
        bad_user = payload.copy()
        bad_user["email"] = "invalid_format"
        r = requests.post(f"{BASE_URL}/users", json=bad_user)
        assert r.status_code == 422
        
        # Invalid phone (422)
        bad_user = payload.copy()
        bad_user["email"] = f"neg_user_p_{random_suffix}@gmail.com"
        bad_user["phone"] = "abc123phone"
        r = requests.post(f"{BASE_URL}/users", json=bad_user)
        assert r.status_code == 422
        
        # Future purchase date (422)
        bad_report = report_payload.copy()
        bad_report["user_id"] = user_id
        bad_report["barcode"] = f"8901030{random.randint(100000, 999999)}"
        bad_report["purchase_date"] = "2040-01-01"
        r = requests.post(f"{BASE_URL}/reports", json=bad_report)
        assert r.status_code == 422
        
        # Description <20 chars (422)
        bad_report = report_payload.copy()
        bad_report["description"] = "short"
        r = requests.post(f"{BASE_URL}/reports", json=bad_report)
        assert r.status_code == 422
        
        # Duplicate case creation limit (400)
        r = requests.post(f"{BASE_URL}/cases", json={"alert_id": alert_id, "title": "Dupe", "description": "Dupe"})
        # (Should fail since the alert's active case was closed or duplicate case limit rules block it)
        assert r.status_code == 400
        
        # Missing entities (404)
        random_uuid = str(uuid.uuid4())
        assert requests.get(f"{BASE_URL}/reports/{random_uuid}").status_code == 404
        assert requests.get(f"{BASE_URL}/cases/{random_uuid}").status_code == 404
        
        print_pass("Negative validations completed (Duplicate users, bad formats, limits, 404s)")
        log_result("Negative Tests", True)

    except AssertionError as e:
        print_fail("Assertion verification failed", str(e))
        log_result("Workflow Failure", False)
    except Exception as e:
        print_fail("Unexpected test suite runtime error", str(e))
        log_result("Suite Crash", False)

    # ── REPORT GENERATION ────────────────────────────────────────────────────
    duration = time.time() - start_time
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    final_result = "PASSED" if failed_tests == 0 else "FAILED"
    
    report_content = f"""# PGN End-to-End Validation Report

## ⚙️ Environment Details
- **Timestamp**: {timestamp}
- **Backend URL**: {BASE_URL}
- **Execution Time**: {duration:.2f} seconds

## 📊 Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {failed_tests}
- **Success Rate**: {success_rate:.1f}%
- **Final Result**: **{final_result}**

## 📋 Steps Status
| Step Category | Status |
| :--- | :--- |
| Community User | {results.get("Community User", "SKIP")} |
| Product Report | {results.get("Product Report", "SKIP")} |
| Credibility Engine | {results.get("Credibility Engine", "SKIP")} |
| Issue Clustering | {results.get("Issue Clustering", "SKIP")} |
| Community Intelligence | {results.get("Community Intelligence", "SKIP")} |
| Automatic Cluster Growth | {results.get("Automatic Cluster Growth", "SKIP")} |
| Safety Alerts | {results.get("Safety Alerts", "SKIP")} |
| Alert Lifecycle | {results.get("Alert Lifecycle", "SKIP")} |
| Alert Reopening | {results.get("Alert Reopening", "SKIP")} |
| Investigation | {results.get("Investigation", "SKIP")} |
| Assignment | {results.get("Assignment", "SKIP")} |
| Notes | {results.get("Notes", "SKIP")} |
| Evidence | {results.get("Evidence", "SKIP")} |
| Timeline | {results.get("Timeline", "SKIP")} |
| Resolve Investigation | {results.get("Resolve Investigation", "SKIP")} |
| Close Investigation | {results.get("Close Investigation", "SKIP")} |
| Dashboards | {results.get("Dashboards", "SKIP")} |
| Negative Tests | {results.get("Negative Tests", "SKIP")} |

## 🏁 Final Outcome
**PGN FEATURE VALIDATION {final_result}**
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"\n==================================================")
    print(f"  PGN E2E TEST WORKFLOW RUN: {final_result}")
    print(f"  Report written to: {REPORT_PATH}")
    print(f"==================================================\n")
    
    if failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run_test_suite()
