"""
003_pgn_phase3.py
Alembic migration: create issue_clusters, cluster_reports,
and cluster_locations tables.

Revision ID: 003_pgn_phase3
Revises: 002_pgn_phase2
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "003_pgn_phase3"
down_revision = "002_pgn_phase2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create issue_clusters table ───────────────────────────────────────
    op.create_table(
        "issue_clusters",
        sa.Column("id",                     UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cluster_code",           sa.String(50),      nullable=False),
        sa.Column("reported_product_id",    UUID(as_uuid=True), nullable=True),
        sa.Column("barcode",                sa.String(100),     nullable=False),
        sa.Column("batch_number",           sa.String(100),     nullable=False),
        sa.Column("primary_issue_type",      sa.String(100),     nullable=False),
        sa.Column("status",                 sa.String(50),      nullable=False, server_default="NEW"),
        sa.Column("severity",               sa.String(50),      nullable=False, server_default="LOW"),
        sa.Column("affected_reports_count", sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("affected_users_count",   sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("affected_cities_count",  sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("first_reported_at",      sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_reported_at",       sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at",             sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",             sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["reported_product_id"], ["public.products.id"],
            name="fk_issue_clusters_reported_product_id",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("cluster_code", name="uq_issue_clusters_cluster_code"),
        schema="community",
    )

    op.create_index("ix_issue_clusters_cluster_code",        "issue_clusters", ["cluster_code"],        schema="community")
    op.create_index("ix_issue_clusters_reported_product_id", "issue_clusters", ["reported_product_id"], schema="community")
    op.create_index("ix_issue_clusters_barcode",             "issue_clusters", ["barcode"],             schema="community")
    op.create_index("ix_issue_clusters_batch_number",        "issue_clusters", ["batch_number"],        schema="community")

    # ── 2. Create cluster_reports table ──────────────────────────────────────
    op.create_table(
        "cluster_reports",
        sa.Column("id",         UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cluster_id", UUID(as_uuid=True), nullable=False),
        sa.Column("report_id",  UUID(as_uuid=True), nullable=False),
        sa.Column("linked_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["cluster_id"], ["community.issue_clusters.id"],
            name="fk_cluster_reports_cluster_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"], ["community.product_reports.id"],
            name="fk_cluster_reports_report_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("report_id", name="uq_cluster_reports_report_id"),
        schema="community",
    )

    op.create_index("ix_cluster_reports_cluster_id", "cluster_reports", ["cluster_id"], schema="community")
    op.create_index("ix_cluster_reports_report_id",  "cluster_reports", ["report_id"],  schema="community")

    # ── 3. Create cluster_locations table ────────────────────────────────────
    op.create_table(
        "cluster_locations",
        sa.Column("id",           UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cluster_id",   UUID(as_uuid=True), nullable=False),
        sa.Column("country",      sa.String(100),     nullable=False),
        sa.Column("state",        sa.String(100),     nullable=False),
        sa.Column("city",         sa.String(100),     nullable=False),
        sa.Column("report_count", sa.Integer(),       nullable=False, server_default="1"),
        sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["cluster_id"], ["community.issue_clusters.id"],
            name="fk_cluster_locations_cluster_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )

    op.create_index("ix_cluster_locations_cluster_id", "cluster_locations", ["cluster_id"], schema="community")


def downgrade() -> None:
    op.drop_index("ix_cluster_locations_cluster_id", table_name="cluster_locations", schema="community")
    op.drop_table("cluster_locations", schema="community")

    op.drop_index("ix_cluster_reports_report_id",  table_name="cluster_reports", schema="community")
    op.drop_index("ix_cluster_reports_cluster_id", table_name="cluster_reports", schema="community")
    op.drop_table("cluster_reports", schema="community")

    op.drop_index("ix_issue_clusters_batch_number",        table_name="issue_clusters", schema="community")
    op.drop_index("ix_issue_clusters_barcode",             table_name="issue_clusters", schema="community")
    op.drop_index("ix_issue_clusters_reported_product_id", table_name="issue_clusters", schema="community")
    op.drop_index("ix_issue_clusters_cluster_code",        table_name="issue_clusters", schema="community")
    op.drop_table("issue_clusters", schema="community")
