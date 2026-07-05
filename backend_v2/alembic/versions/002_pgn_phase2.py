"""
002_pgn_phase2.py
Alembic migration: create the 'community.report_credibility' table
with columns, constraints, and indexes.

Revision ID: 002_pgn_phase2
Revises: 001_pgn_phase1
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "002_pgn_phase2"
down_revision = "001_pgn_phase1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create report_credibility table ───────────────────────────────────
    op.create_table(
        "report_credibility",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("report_id",           UUID(as_uuid=True), nullable=False),
        sa.Column("barcode_verified",    sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("batch_verified",      sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("images_uploaded",     sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("receipt_uploaded",    sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("verified_user",       sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("description_length",  sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("duplicate_reports",   sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("location_available",  sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("purchase_date_valid", sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("score",               sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("credibility_level",   sa.String(20),      nullable=False),
        sa.Column("calculated_at",       sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        
        sa.ForeignKeyConstraint(
            ["report_id"], ["community.product_reports.id"],
            name="fk_report_credibility_report_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("report_id", name="uq_report_credibility_report_id"),
        schema="community",
    )

    # ── 2. Create Indexes ───────────────────────────────────────────────────
    op.create_index("ix_report_credibility_report_id",        "report_credibility", ["report_id"],        schema="community")
    op.create_index("ix_report_credibility_score",            "report_credibility", ["score"],            schema="community")
    op.create_index("ix_report_credibility_credibility_level", "report_credibility", ["credibility_level"], schema="community")


def downgrade() -> None:
    # ── 1. Drop Indexes ─────────────────────────────────────────────────────
    op.drop_index("ix_report_credibility_credibility_level", table_name="report_credibility", schema="community")
    op.drop_index("ix_report_credibility_score",             table_name="report_credibility", schema="community")
    op.drop_index("ix_report_credibility_report_id",         table_name="report_credibility", schema="community")

    # ── 2. Drop Table ───────────────────────────────────────────────────────
    op.drop_table("report_credibility", schema="community")
