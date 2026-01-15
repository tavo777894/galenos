"""add index on patients.deleted_at

Revision ID: acde1d2e3f4a
Revises: f1e2d3c4b5a6
Create Date: 2026-01-15 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'acde1d2e3f4a'
down_revision: Union[str, None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_patients_deleted_at'), 'patients', ['deleted_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_patients_deleted_at'), table_name='patients')
