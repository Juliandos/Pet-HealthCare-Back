"""Fix audit_logs foreign key to allow SET NULL on delete

Revision ID: fix_audit_logs_fk
Revises: 46e6678291ad
Create Date: 2025-01-27 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_audit_logs_fk'
down_revision: Union[str, Sequence[str], None] = '46e6678291ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Primero eliminar la constraint existente
    op.drop_constraint(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        type_='foreignkey',
        schema='petcare'
    )
    
    # Crear la nueva constraint con ON DELETE SET NULL
    op.create_foreign_key(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        'users',
        ['actor_user_id'],
        ['id'],
        ondelete='SET NULL',
        source_schema='petcare',
        referent_schema='petcare'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar la constraint con SET NULL
    op.drop_constraint(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        type_='foreignkey',
        schema='petcare'
    )
    
    # Recrear la constraint sin ON DELETE (comportamiento por defecto)
    op.create_foreign_key(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        'users',
        ['actor_user_id'],
        ['id'],
        source_schema='petcare',
        referent_schema='petcare'
    )

