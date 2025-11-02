"""Add product category and fields

Revision ID: f1g2h3i4j5k6
Revises: e6f7g8h9i0j1
Create Date: 2025-11-02 16:50:00.000000

"""

from alembic import op  # type: ignore
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1g2h3i4j5k6"
down_revision = "e6f7g8h9i0j1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add category column with index
    op.add_column(
        "product",
        sa.Column("category", sa.String(), nullable=False, server_default="general"),
    )
    op.create_index(op.f("ix_product_category"), "product", ["category"], unique=False)

    # Add description column
    op.add_column("product", sa.Column("description", sa.String(), nullable=True))

    # Add image_url column
    op.add_column("product", sa.Column("image_url", sa.String(), nullable=True))

    # Add stock column
    op.add_column(
        "product",
        sa.Column("stock", sa.Integer(), nullable=False, server_default="100"),
    )


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column("product", "stock")
    op.drop_column("product", "image_url")
    op.drop_column("product", "description")
    op.drop_index(op.f("ix_product_category"), table_name="product")
    op.drop_column("product", "category")
