"""add cascade to project member project foreign key

Revision ID: 9d4f2c1a8b6e
Revises: 45de3c47039d
Create Date: 2026-05-09 16:25:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9d4f2c1a8b6e"
down_revision: Union[str, Sequence[str], None] = "45de3c47039d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "project_members_project_id_fkey",
        "project_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "project_members_project_id_fkey",
        "project_members",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "project_members_project_id_fkey",
        "project_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "project_members_project_id_fkey",
        "project_members",
        "projects",
        ["project_id"],
        ["id"],
    )
