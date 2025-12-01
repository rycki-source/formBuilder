"""add form types

Revision ID: 002_add_form_types
Revises: 001_initial_schema
Create Date: 2025-11-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_form_types'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajouter les colonnes type_structurel et type_fonctionnel
    op.add_column('formulaire', sa.Column('type_structurel', sa.String(length=50), nullable=False, server_default='simple'))
    op.add_column('formulaire', sa.Column('type_fonctionnel', sa.String(length=50), nullable=False, server_default='personnalise'))


def downgrade() -> None:
    # Supprimer les colonnes en cas de rollback
    op.drop_column('formulaire', 'type_fonctionnel')
    op.drop_column('formulaire', 'type_structurel')
