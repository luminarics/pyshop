"""Add Order and OrderItem tables for checkout

Revision ID: e6f7g8h9i0j1
Revises: a1b2c3d4e5f6
Create Date: 2025-10-25 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e6f7g8h9i0j1"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create order table
    op.create_table(
        "order",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payment_status", sa.String(length=20), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("tax", sa.Float(), nullable=False),
        sa.Column("shipping_cost", sa.Float(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("shipping_name", sa.String(length=255), nullable=False),
        sa.Column("shipping_email", sa.String(length=255), nullable=False),
        sa.Column("shipping_phone", sa.String(length=50), nullable=True),
        sa.Column("shipping_address", sa.Text(), nullable=False),
        sa.Column("shipping_city", sa.String(length=100), nullable=False),
        sa.Column("shipping_state", sa.String(length=100), nullable=True),
        sa.Column("shipping_postal_code", sa.String(length=20), nullable=False),
        sa.Column("shipping_country", sa.String(length=100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("shipped_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create indexes for order table
    op.create_index(op.f("ix_order_user_id"), "order", ["user_id"])
    op.create_index(
        op.f("ix_order_order_number"), "order", ["order_number"], unique=True
    )
    op.create_index("idx_order_user_status", "order", ["user_id", "status"])
    op.create_index("idx_order_created_at", "order", ["created_at"])
    op.create_index("idx_order_status", "order", ["status"])

    # Create order_item table
    op.create_table(
        "order_item",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["order_id"], ["order.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="RESTRICT"),
    )

    # Create indexes for order_item table
    op.create_index("idx_orderitem_order_id", "order_item", ["order_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop order_item table and its indexes
    op.drop_index("idx_orderitem_order_id", table_name="order_item")
    op.drop_table("order_item")

    # Drop order table and its indexes
    op.drop_index("idx_order_status", table_name="order")
    op.drop_index("idx_order_created_at", table_name="order")
    op.drop_index("idx_order_user_status", table_name="order")
    op.drop_index(op.f("ix_order_order_number"), table_name="order")
    op.drop_index(op.f("ix_order_user_id"), table_name="order")
    op.drop_table("order")
