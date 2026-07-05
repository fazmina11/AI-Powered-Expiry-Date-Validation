"""
006_pgn_phase6.py
Alembic migration: create investigation_cases, investigation_notes,
case_evidence, and case_timeline tables.

Revision ID: 006_pgn_phase6
Revises: 005_pgn_phase5
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "006_pgn_phase6"
down_revision = "005_pgn_phase5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create investigation_cases table ──────────────────────────────────
    op.create_table(
        "investigation_cases",
        sa.Column("id",               UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_number",      sa.String(50),      nullable=False),
        sa.Column("alert_id",         UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_id",       UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_officer", sa.String(100),     nullable=True),
        sa.Column("priority",         sa.String(50),      nullable=False, server_default="MEDIUM"),
        sa.Column("status",           sa.String(50),      nullable=False, server_default="OPEN"),
        sa.Column("title",            sa.String(255),     nullable=False),
        sa.Column("description",      sa.Text(),          nullable=False),
        sa.Column("opened_at",        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("due_date",         sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at",        sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution",       sa.Text(),          nullable=True),
        sa.Column("final_decision",   sa.String(50),      nullable=True),
        sa.Column("created_at",       sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",       sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["alert_id"], ["community.safety_alerts.id"],
            name="fk_investigation_cases_alert_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["cluster_id"], ["community.issue_clusters.id"],
            name="fk_investigation_cases_cluster_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("case_number", name="uq_investigation_cases_case_number"),
        schema="community",
    )

    op.create_index("ix_investigation_cases_alert_id",         "investigation_cases", ["alert_id"],         schema="community")
    op.create_index("ix_investigation_cases_cluster_id",       "investigation_cases", ["cluster_id"],       schema="community")
    op.create_index("ix_investigation_cases_priority",         "investigation_cases", ["priority"],         schema="community")
    op.create_index("ix_investigation_cases_status",           "investigation_cases", ["status"],           schema="community")
    op.create_index("ix_investigation_cases_assigned_officer", "investigation_cases", ["assigned_officer"], schema="community")
    op.create_index("ix_investigation_cases_created_at",       "investigation_cases", ["created_at"],       schema="community")

    # ── 2. Create investigation_notes table ──────────────────────────────────
    op.create_table(
        "investigation_notes",
        sa.Column("id",         UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id",    UUID(as_uuid=True), nullable=False),
        sa.Column("note",       sa.Text(),          nullable=False),
        sa.Column("created_by", sa.String(100),     nullable=False, server_default="SYSTEM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["case_id"], ["community.investigation_cases.id"],
            name="fk_investigation_notes_case_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_investigation_notes_case_id", "investigation_notes", ["case_id"], schema="community")

    # ── 3. Create case_evidence table ────────────────────────────────────────
    op.create_table(
        "case_evidence",
        sa.Column("id",            UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id",       UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_type", sa.String(50),      nullable=False, server_default="IMAGE"),
        sa.Column("file_url",      sa.Text(),          nullable=False),
        sa.Column("description",   sa.Text(),          nullable=False),
        sa.Column("uploaded_by",   sa.String(100),     nullable=False, server_default="SYSTEM"),
        sa.Column("uploaded_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["case_id"], ["community.investigation_cases.id"],
            name="fk_case_evidence_case_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_case_evidence_case_id", "case_evidence", ["case_id"], schema="community")

    # ── 4. Create case_timeline table ────────────────────────────────────────
    op.create_table(
        "case_timeline",
        sa.Column("id",                UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id",           UUID(as_uuid=True), nullable=False),
        sa.Column("event_type",        sa.String(100),     nullable=False),
        sa.Column("event_description", sa.Text(),          nullable=False),
        sa.Column("performed_by",      sa.String(100),     nullable=False, server_default="SYSTEM"),
        sa.Column("created_at",        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["case_id"], ["community.investigation_cases.id"],
            name="fk_case_timeline_case_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_case_timeline_case_id", "case_timeline", ["case_id"], schema="community")


def downgrade() -> None:
    op.drop_index("ix_case_timeline_case_id", table_name="case_timeline", schema="community")
    op.drop_table("case_timeline", schema="community")

    op.drop_index("ix_case_evidence_case_id", table_name="case_evidence", schema="community")
    op.drop_table("case_evidence", schema="community")

    op.drop_index("ix_investigation_notes_case_id", table_name="investigation_notes", schema="community")
    op.drop_table("investigation_notes", schema="community")

    op.drop_index("ix_investigation_cases_created_at",       table_name="investigation_cases", schema="community")
    op.drop_index("ix_investigation_cases_assigned_officer", table_name="investigation_cases", schema="community")
    op.drop_index("ix_investigation_cases_status",           table_name="investigation_cases", schema="community")
    op.drop_index("ix_investigation_cases_priority",         table_name="investigation_cases", schema="community")
    op.drop_index("ix_investigation_cases_cluster_id",       table_name="investigation_cases", schema="community")
    op.drop_index("ix_investigation_cases_alert_id",         table_name="investigation_cases", schema="community")
    op.drop_table("investigation_cases", schema="community")
