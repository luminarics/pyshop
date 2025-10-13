"""Add avatar_url to user

Revision ID: a1b2c3d4e5f6
Revises: 709691f8a05f
Create Date: 2025-10-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "709691f8a05f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add avatar_url column to user table
    op.add_column("user", sa.Column("avatar_url", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove avatar_url column from user table
    op.drop_column("user", "avatar_url")
