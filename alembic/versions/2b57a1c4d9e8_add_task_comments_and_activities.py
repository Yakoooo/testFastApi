"""add task comments and activities

Revision ID: 2b57a1c4d9e8
Revises: 10e8a2968ceb
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b57a1c4d9e8"
down_revision: Union[str, Sequence[str], None] = "10e8a2968ceb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "task_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_comments_author_id"), "task_comments", ["author_id"], unique=False)
    op.create_index(op.f("ix_task_comments_id"), "task_comments", ["id"], unique=False)
    op.create_index(op.f("ix_task_comments_task_id"), "task_comments", ["task_id"], unique=False)

    op.create_table(
        "task_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("field", sa.String(length=50), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_activities_action"), "task_activities", ["action"], unique=False)
    op.create_index(op.f("ix_task_activities_actor_id"), "task_activities", ["actor_id"], unique=False)
    op.create_index(op.f("ix_task_activities_id"), "task_activities", ["id"], unique=False)
    op.create_index(op.f("ix_task_activities_task_id"), "task_activities", ["task_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_task_activities_task_id"), table_name="task_activities")
    op.drop_index(op.f("ix_task_activities_id"), table_name="task_activities")
    op.drop_index(op.f("ix_task_activities_actor_id"), table_name="task_activities")
    op.drop_index(op.f("ix_task_activities_action"), table_name="task_activities")
    op.drop_table("task_activities")

    op.drop_index(op.f("ix_task_comments_task_id"), table_name="task_comments")
    op.drop_index(op.f("ix_task_comments_id"), table_name="task_comments")
    op.drop_index(op.f("ix_task_comments_author_id"), table_name="task_comments")
    op.drop_table("task_comments")
