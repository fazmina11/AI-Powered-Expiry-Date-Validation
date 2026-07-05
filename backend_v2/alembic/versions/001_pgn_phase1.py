"""
001_create_community_schema.py
Alembic migration: create the 'community' PostgreSQL schema
and the three PGN Phase 1 tables.

Revision ID: 001_pgn_phase1
Revises: (none — first PGN migration)
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Alembic revision identifiers
revision = "001_pgn_phase1"
down_revision = None   # set to the current head if chaining
branch_labels = ("pgn",)
depends_on = None


def upgrade() -> None:
    # ── 1. Create the community schema ──────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS community")

    # Enable pgcrypto for gen_random_uuid() if not already active
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ── 2. Enums (created inside community schema) ───────────────────────────
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'report_type_enum'
                           AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'community'))
            THEN
                CREATE TYPE community.report_type_enum AS ENUM (
                    'DAMAGED_PACKAGING', 'WRONG_EXPIRY', 'BAD_SMELL', 'LEAKAGE',
                    'WRONG_PRODUCT', 'FOREIGN_OBJECT', 'FAKE_PRODUCT', 'OTHER'
                );
            END IF;
        END
        $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severity_enum'
                           AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'community'))
            THEN
                CREATE TYPE community.severity_enum AS ENUM (
                    'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
                );
            END IF;
        END
        $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'report_status_enum'
                           AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'community'))
            THEN
                CREATE TYPE community.report_status_enum AS ENUM (
                    'PENDING', 'UNDER_REVIEW', 'VERIFIED', 'REJECTED'
                );
            END IF;
        END
        $$;
    """)

    # ── 3. community_users ───────────────────────────────────────────────────
    op.create_table(
        "community_users",
        sa.Column("id",          UUID(as_uuid=True),   primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name",   sa.String(255),        nullable=False),
        sa.Column("email",       sa.String(320),        nullable=False),
        sa.Column("phone",       sa.String(30),         nullable=True),
        sa.Column("is_verified", sa.Boolean(),          nullable=False, server_default="false"),
        sa.Column("country",     sa.String(100),        nullable=True),
        sa.Column("state",       sa.String(100),        nullable=True),
        sa.Column("city",        sa.String(100),        nullable=True),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="community",
    )
    op.create_unique_constraint("uq_community_users_email", "community_users", ["email"], schema="community")
    op.create_index("ix_community_users_email", "community_users", ["email"], schema="community")

    # ── 4. product_reports ───────────────────────────────────────────────────
    op.create_table(
        "product_reports",
        sa.Column("id",                UUID(as_uuid=True),   primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id",           UUID(as_uuid=True),   nullable=False),
        sa.Column("barcode",           sa.String(100),        nullable=False),
        sa.Column("batch_number",      sa.String(100),        nullable=False),
        sa.Column("product_name",      sa.String(255),        nullable=True),
        sa.Column("report_type",       sa.Text(),             nullable=False),   # backed by enum at app layer
        sa.Column("severity",          sa.Text(),             nullable=False),
        sa.Column("description",       sa.Text(),             nullable=False),
        sa.Column("purchase_location", sa.String(255),        nullable=True),
        sa.Column("purchase_date",     sa.Date(),             nullable=True),
        sa.Column("status",            sa.Text(),             nullable=False, server_default="PENDING"),
        sa.Column("created_at",        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["community.community_users.id"],
            name="fk_product_reports_user_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )
    op.create_index("ix_product_reports_user_id", "product_reports", ["user_id"], schema="community")
    op.create_index("ix_product_reports_barcode",  "product_reports", ["barcode"],  schema="community")

    # ── 5. report_images ─────────────────────────────────────────────────────
    op.create_table(
        "report_images",
        sa.Column("id",          UUID(as_uuid=True),   primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("report_id",   UUID(as_uuid=True),   nullable=False),
        sa.Column("image_url",   sa.Text(),             nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["report_id"], ["community.product_reports.id"],
            name="fk_report_images_report_id",
            ondelete="CASCADE",
        ),
        schema="community",
    )
    op.create_index("ix_report_images_report_id", "report_images", ["report_id"], schema="community")


def downgrade() -> None:
    op.drop_table("report_images",    schema="community")
    op.drop_table("product_reports",  schema="community")
    op.drop_table("community_users",  schema="community")
    op.execute("DROP TYPE IF EXISTS community.report_status_enum")
    op.execute("DROP TYPE IF EXISTS community.severity_enum")
    op.execute("DROP TYPE IF EXISTS community.report_type_enum")
    op.execute("DROP SCHEMA IF EXISTS community CASCADE")
