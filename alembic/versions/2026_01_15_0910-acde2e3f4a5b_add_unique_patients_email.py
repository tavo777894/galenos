"""add unique constraint on patients.email

NOTE: If production data contains duplicate patient emails, this migration will fail.

Revision ID: acde2e3f4a5b
Revises: acde1d2e3f4a
Create Date: 2026-01-15 09:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'acde2e3f4a5b'
down_revision: Union[str, None] = 'acde1d2e3f4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_patients_email', 'patients', ['email'])


def downgrade() -> None:
    op.drop_constraint('uq_patients_email', 'patients', type_='unique')
