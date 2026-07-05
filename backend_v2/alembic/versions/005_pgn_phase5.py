"""
005_pgn_phase5.py
Alembic migration: create safety_alerts, alert_history,
and alert_notifications tables.

Revision ID: 005_pgn_phase5
Revises: 004_pgn_phase4
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "005_pgn_phase5"
down_revision = "004_pgn_phase4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create safety_alerts table ────────────────────────────────────────
    op.create_table(
        "safety_alerts",
        sa.Column("id",                 UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("alert_code",         sa.String(50),      nullable=False),
        sa.Column("cluster_id",         UUID(as_uuid=True), nullable=False),
        sa.Column("alert_level",         sa.String(50),      nullable=False, server_default="INFORMATION"),
        sa.Column("status",             sa.String(50),      nullable=False, server_default="ACTIVE"),
        sa.Column("title",              sa.String(255),     nullable=False),
        sa.Column("description",        sa.Text(),          nullable=False),
        sa.Column("recommended_action",  sa.Text(),          nullable=False),
        sa.Column("generated_reason",   sa.Text(),          nullable=False),
        sa.Column("generated_by",       sa.String(100),     nullable=False, server_default="SYSTEM"),
        sa.Column("risk_score",         sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("affected_reports",   sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("affected_users",     sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("affected_cities",    sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("created_at",         sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",         sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at",        sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(
            ["cluster_id"], ["community.issue_clusters.id"],
            name="fk_safety_alerts_cluster_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("alert_code", name="uq_safety_alerts_alert_code"),
        schema="community",
    )

    op.create_index("ix_safety_alerts_cluster_id", "safety_alerts", ["cluster_id"], schema="community")
    op.create_index("ix_safety_alerts_alert_level", "safety_alerts", ["alert_level"], schema="community")
    op.create_index("ix_safety_alerts_status",      "safety_alerts", ["status"],      schema="community")
    op.create_index("ix_safety_alerts_created_at",  "safety_alerts", ["created_at"],  schema="community")
    op.create_index("ix_safety_alerts_risk_score",  "safety_alerts", ["risk_score"],  schema="community")

    # ── 2. Create alert_history table ────────────────────────────────────────
    op.create_table(
        "alert_history",
        sa.Column("id",         UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("alert_id",   UUID(as_uuid=True), nullable=False),
        sa.Column("old_status", sa.String(50),      nullable=True),
        sa.Column("new_status", sa.String(50),      nullable=False),
        sa.Column("remarks",    sa.Text(),          nullable=True),
        sa.Column("changed_by", sa.String(100),     nullable=False, server_default="SYSTEM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["alert_id"], ["community.safety_alerts.id"],
            name="fk_alert_history_alert_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_alert_history_alert_id", "alert_history", ["alert_id"], schema="community")

    # ── 3. Create alert_notifications table ──────────────────────────────────
    op.create_table(
        "alert_notifications",
        sa.Column("id",                UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("alert_id",          UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(50),      nullable=False),
        sa.Column("recipient",         sa.String(255),     nullable=False),
        sa.Column("delivery_status",   sa.String(50),      nullable=False, server_default="SENT"),
        sa.Column("sent_at",           sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["alert_id"], ["community.safety_alerts.id"],
            name="fk_alert_notifications_alert_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_alert_notifications_alert_id", "alert_notifications", ["alert_id"], schema="community")


def downgrade() -> None:
    op.drop_index("ix_alert_notifications_alert_id", table_name="alert_notifications", schema="community")
    op.drop_table("alert_notifications", schema="community")

    op.drop_index("ix_alert_history_alert_id", table_name="alert_history", schema="community")
    op.drop_table("alert_history", schema="community")

    op.drop_index("ix_safety_alerts_risk_score",  table_name="safety_alerts", schema="community")
    op.drop_index("ix_safety_alerts_created_at",  table_name="safety_alerts", schema="community")
    op.drop_index("ix_safety_alerts_status",      table_name="safety_alerts", schema="community")
    op.drop_index("ix_safety_alerts_alert_level", table_name="safety_alerts", schema="community")
    op.drop_index("ix_safety_alerts_cluster_id",   table_name="safety_alerts", schema="community")
    op.drop_table("safety_alerts", schema="community")
