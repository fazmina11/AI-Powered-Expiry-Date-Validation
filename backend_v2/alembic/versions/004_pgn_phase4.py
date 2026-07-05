"""
004_pgn_phase4.py
Alembic migration: create the 'community.cluster_intelligence' table.

Revision ID: 004_pgn_phase4
Revises: 003_pgn_phase3
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "004_pgn_phase4"
down_revision = "003_pgn_phase3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create cluster_intelligence table ─────────────────────────────────
    op.create_table(
        "cluster_intelligence",
        sa.Column("id",                   UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cluster_id",           UUID(as_uuid=True), nullable=False),
        sa.Column("risk_score",           sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("growth_rate",          sa.Float(),         nullable=False, server_default="0.0"),
        sa.Column("activity_level",       sa.String(30),      nullable=False, server_default="LOW"),
        sa.Column("trend",                sa.String(30),      nullable=False, server_default="STABLE"),
        sa.Column("spread_level",         sa.String(30),      nullable=False, server_default="LOCAL"),
        sa.Column("escalation_level",     sa.String(30),      nullable=False, server_default="NONE"),
        sa.Column("reports_last_24h",     sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("reports_last_7_days",  sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("reports_last_30_days", sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("new_cities",           sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("average_credibility",  sa.Float(),         nullable=False, server_default="0.0"),
        sa.Column("is_trending",          sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("last_calculated",      sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["cluster_id"], ["community.issue_clusters.id"],
            name="fk_cluster_intelligence_cluster_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("cluster_id", name="uq_cluster_intelligence_cluster_id"),
        schema="community",
    )

    # ── 2. Create Indexes ───────────────────────────────────────────────────
    op.create_index("ix_cluster_intelligence_cluster_id",   "cluster_intelligence", ["cluster_id"],   schema="community")
    op.create_index("ix_cluster_intelligence_risk_score",   "cluster_intelligence", ["risk_score"],   schema="community")
    op.create_index("ix_cluster_intelligence_trend",        "cluster_intelligence", ["trend"],        schema="community")
    op.create_index("ix_cluster_intelligence_activity_level", "cluster_intelligence", ["activity_level"], schema="community")
    op.create_index("ix_cluster_intelligence_spread_level", "cluster_intelligence", ["spread_level"], schema="community")
    op.create_index("ix_cluster_intelligence_is_trending",   "cluster_intelligence", ["is_trending"],   schema="community")


def downgrade() -> None:
    # ── 1. Drop Indexes ─────────────────────────────────────────────────────
    op.drop_index("ix_cluster_intelligence_is_trending",   table_name="cluster_intelligence", schema="community")
    op.drop_index("ix_cluster_intelligence_spread_level", table_name="cluster_intelligence", schema="community")
    op.drop_index("ix_cluster_intelligence_activity_level", table_name="cluster_intelligence", schema="community")
    op.drop_index("ix_cluster_intelligence_trend",        table_name="cluster_intelligence", schema="community")
    op.drop_index("ix_cluster_intelligence_risk_score",   table_name="cluster_intelligence", schema="community")
    op.drop_index("ix_cluster_intelligence_cluster_id",   table_name="cluster_intelligence", schema="community")

    # ── 2. Drop Table ───────────────────────────────────────────────────────
    op.drop_table("cluster_intelligence", schema="community")
