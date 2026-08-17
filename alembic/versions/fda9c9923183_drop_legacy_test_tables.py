"""drop legacy test tables

Revision ID: fda9c9923183
Revises: 20260615_merge_cost_heads
Create Date: 2026-08-16 20:16:03.018570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = 'fda9c9923183'
down_revision: Union[str, None] = '20260615_merge_cost_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop legacy single-run test tables (replaced by prompt_test_* engine)."""

    op.drop_table("metrics")
    op.drop_table("results")
    op.drop_table("test_runs")


def downgrade() -> None:
    """Recreate legacy test tables (no-op for reference clone: upstream owns history)."""

    pass
