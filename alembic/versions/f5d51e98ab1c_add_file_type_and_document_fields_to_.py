"""add_file_type_and_document_fields_to_pet_photos

Revision ID: f5d51e98ab1c
Revises: 46e6678291ad
Create Date: 2025-12-08 14:53:53.288031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5d51e98ab1c'
down_revision: Union[str, Sequence[str], None] = '46e6678291ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar campo file_type con valor por defecto 'image' para registros existentes
    op.add_column('pet_photos', 
        sa.Column('file_type', sa.String(), nullable=False, server_default='image'),
        schema='petcare'
    )
    
    # Agregar campo document_category (nullable)
    op.add_column('pet_photos',
        sa.Column('document_category', sa.String(), nullable=True),
        schema='petcare'
    )
    
    # Agregar campo description (nullable, TEXT)
    op.add_column('pet_photos',
        sa.Column('description', sa.Text(), nullable=True),
        schema='petcare'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar los campos agregados
    op.drop_column('pet_photos', 'description', schema='petcare')
    op.drop_column('pet_photos', 'document_category', schema='petcare')
    op.drop_column('pet_photos', 'file_type', schema='petcare')
