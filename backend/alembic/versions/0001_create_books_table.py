"""create books table

Revision ID: 0001
Revises:
Create Date: 2026-10-15
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("author", sa.String(120), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="to-read"),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_books_id", "books", ["id"])


def downgrade():
    op.drop_index("ix_books_id", table_name="books")
    op.drop_table("books")
