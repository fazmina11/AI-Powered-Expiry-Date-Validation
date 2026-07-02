"""
models/audit_log.py — Immutable event log for every significant action.

Append-only. Never updated. Provides a full history of:
  - who did what
  - on which record
  - at what time
  - what changed (before/after JSON snapshots)

Used for compliance, debugging, and ML team traceability.
"""

import uuid

from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # ── What happened ─────────────────────────────────────────
    event_type      = Column(String(100), nullable=False, index=True)
    # e.g. product.created | inventory.intake | ocr.completed
    #       ml.prediction_received | manual_review.completed | status.changed

    # ── Which record ─────────────────────────────────────────
    entity_type     = Column(String(100), nullable=True)   # product | inventory_item | ocr_result
    entity_id       = Column(String(100), nullable=True, index=True)  # UUID as string
    action          = Column(String(100), nullable=True, index=True)
    message         = Column(Text, nullable=True)
    metadata_json   = Column(JSONB, nullable=True)

    # ── Who did it ────────────────────────────────────────────
    actor_id        = Column(String(200), nullable=True)   # user_id, service_name, "system"
    actor_name      = Column(String(150), nullable=True)
    actor_type      = Column(String(50),  nullable=True)   # user | service | ml_team | system

    # ── What changed ─────────────────────────────────────────
    before_state    = Column(JSON, nullable=True)   # snapshot before the change
    after_state     = Column(JSON, nullable=True)   # snapshot after the change
    change_summary  = Column(Text, nullable=True)   # human-readable description

    # ── Request context ───────────────────────────────────────
    ip_address      = Column(String(50),  nullable=True)
    user_agent      = Column(String(500), nullable=True)
    request_id      = Column(String(100), nullable=True)

    # ── Timestamp — immutable, set once ──────────────────────
    occurred_at     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
