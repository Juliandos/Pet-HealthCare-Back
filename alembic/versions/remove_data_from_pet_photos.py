"""Remove data column from pet_photos

Revision ID: remove_data_pet_photos
Revises: add_is_profile_pet_photos
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_data_pet_photos'
down_revision: Union[str, Sequence[str], None] = 'add_is_profile_pet_photos'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove data column from pet_photos table."""
    # Eliminar columna data (no se está usando, las imágenes están en S3)
    op.drop_column('pet_photos', 'data', schema='petcare')


def downgrade() -> None:
    """Add data column back to pet_photos table."""
    # Agregar columna data de vuelta (opcional, para rollback)
    op.add_column(
        'pet_photos',
        sa.Column('data', sa.LargeBinary(), nullable=True),
        schema='petcare'
    )

