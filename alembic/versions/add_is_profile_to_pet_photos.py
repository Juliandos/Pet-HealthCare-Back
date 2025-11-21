"""Add is_profile field to pet_photos

Revision ID: add_is_profile_pet_photos
Revises: 46e6678291ad
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_profile_pet_photos'
down_revision: Union[str, Sequence[str], None] = '46e6678291ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_profile column to pet_photos table."""
    # Agregar columna is_profile con valor por defecto False
    op.add_column(
        'pet_photos',
        sa.Column('is_profile', sa.Boolean(), nullable=False, server_default='false'),
        schema='petcare'
    )
    
    # Crear índice para mejorar búsquedas de fotos de perfil
    op.create_index(
        'idx_pet_photos_is_profile',
        'pet_photos',
        ['pet_id', 'is_profile'],
        unique=False,
        schema='petcare'
    )


def downgrade() -> None:
    """Remove is_profile column from pet_photos table."""
    # Eliminar índice
    op.drop_index('idx_pet_photos_is_profile', table_name='pet_photos', schema='petcare')
    
    # Eliminar columna
    op.drop_column('pet_photos', 'is_profile', schema='petcare')

