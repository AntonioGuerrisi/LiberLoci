"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Locations
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("room", sa.String(), nullable=False),
        sa.Column("shelf", sa.String(), nullable=True),
        sa.Column("level", sa.String(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
    )

    # Books
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.String(), nullable=False),
        sa.Column("isbn13", sa.String(13), nullable=True),
        sa.Column("isbn10", sa.String(10), nullable=True),
        sa.Column("publisher", sa.String(), nullable=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("format", sa.String(), nullable=False, server_default="paper"),
        sa.Column("reading_status", sa.String(), nullable=False, server_default="to_read"),
        sa.Column("tags", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("provider_raw_json", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Partial unique index on isbn13 (where not null)
    op.create_index("ix_books_isbn13_unique", "books", ["isbn13"], unique=True, postgresql_where=sa.text("isbn13 IS NOT NULL"))
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_authors", "books", ["authors"])

    # Covers
    op.create_table(
        "covers",
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False, server_default="image/jpeg"),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("covers")
    op.drop_index("ix_books_authors", table_name="books")
    op.drop_index("ix_books_title", table_name="books")
    op.drop_index("ix_books_isbn13_unique", table_name="books")
    op.drop_table("books")
    op.drop_table("locations")
