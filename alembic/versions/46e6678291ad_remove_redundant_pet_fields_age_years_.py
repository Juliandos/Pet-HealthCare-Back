"""Remove redundant pet fields (age_years, photo_url, photo_bytea)

Revision ID: 46e6678291ad
Revises: 
Create Date: 2025-11-19 21:59:59.529910
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46e6678291ad'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('pets', 'age_years', schema='petcare')
    op.drop_column('pets', 'photo_url', schema='petcare')
    op.drop_column('pets', 'photo_bytea', schema='petcare')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('pets', sa.Column('age_years', sa.Integer()), schema='petcare')
    op.add_column('pets', sa.Column('photo_url', sa.String()), schema='petcare')
    op.add_column('pets', sa.Column('photo_bytea', sa.LargeBinary()), schema='petcare')
