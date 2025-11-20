"""Fix audit_logs and password_resets foreign keys for user deletion

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
    # 1. Corregir audit_logs: permitir NULL cuando se elimina el usuario
    op.drop_constraint(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        type_='foreignkey',
        schema='petcare'
    )
    
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
    
    # 2. Corregir password_resets: eliminar en cascada cuando se elimina el usuario
    op.drop_constraint(
        'password_resets_user_id_fkey',
        'password_resets',
        type_='foreignkey',
        schema='petcare'
    )
    
    op.create_foreign_key(
        'password_resets_user_id_fkey',
        'password_resets',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
        source_schema='petcare',
        referent_schema='petcare'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir audit_logs
    op.drop_constraint(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        type_='foreignkey',
        schema='petcare'
    )
    
    op.create_foreign_key(
        'audit_logs_actor_user_id_fkey',
        'audit_logs',
        'users',
        ['actor_user_id'],
        ['id'],
        source_schema='petcare',
        referent_schema='petcare'
    )
    
    # Revertir password_resets
    op.drop_constraint(
        'password_resets_user_id_fkey',
        'password_resets',
        type_='foreignkey',
        schema='petcare'
    )
    
    op.create_foreign_key(
        'password_resets_user_id_fkey',
        'password_resets',
        'users',
        ['user_id'],
        ['id'],
        source_schema='petcare',
        referent_schema='petcare'
    )

