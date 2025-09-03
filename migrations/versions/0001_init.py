from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import uuid


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("payer_id", sa.String(length=64), nullable=False),
        sa.Column("provider_npi", sa.String(length=20), nullable=True),
        sa.Column("status", sa.Enum("queued", "running", "succeeded", "failed", name="runstatus"), nullable=False, server_default="queued"),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=True),
        sa.Column("output_payload", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "idempotent_runs",
        sa.Column("key", sa.String(length=512), primary_key=True),
        sa.Column("run_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_idempotent_runs_run_id", "idempotent_runs", ["run_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_idempotent_runs_run_id", table_name="idempotent_runs")
    op.drop_table("idempotent_runs")
    op.drop_table("runs")

