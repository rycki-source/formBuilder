"""Add dynamic form fields to referentiel

Revision ID: 002_dynamic_forms
Revises: 001_initial
Create Date: 2025-12-05

"""
from alembic import op # type: ignore
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_dynamic_forms'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """
    Ajouter les nouveaux champs pour le système de formulaires dynamiques.
    """
    # Vérifier si les colonnes existent déjà avant de les ajouter
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('referentiel')]
    
    # Ajouter les nouvelles colonnes seulement si elles n'existent pas
    if 'ref_id' not in existing_columns:
        op.add_column('referentiel', sa.Column('ref_id', sa.String(100), nullable=True))
    
    if 'config' not in existing_columns:
        op.add_column('referentiel', sa.Column('config', postgresql.JSONB(), nullable=True))
    
    if 'custom_validators' not in existing_columns:
        op.add_column('referentiel', sa.Column('custom_validators', postgresql.JSONB(), nullable=True))
    
    if 'custom_components' not in existing_columns:
        op.add_column('referentiel', sa.Column('custom_components', postgresql.JSONB(), nullable=True))
    
    if 'tags' not in existing_columns:
        op.add_column('referentiel', sa.Column('tags', postgresql.JSONB(), nullable=True))
    
    if 'is_template' not in existing_columns:
        op.add_column('referentiel', sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'))
    
    if 'is_active' not in existing_columns:
        op.add_column('referentiel', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    if 'source_file' not in existing_columns:
        op.add_column('referentiel', sa.Column('source_file', sa.String(255), nullable=True))
    
    if 'updated_at' not in existing_columns:
        op.add_column('referentiel', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Créer les index s'ils n'existent pas
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('referentiel')]
    
    if 'ix_referentiel_ref_id' not in existing_indexes:
        op.create_index(
            'ix_referentiel_ref_id',
            'referentiel',
            ['ref_id'],
            unique=True,
            postgresql_where=sa.text('ref_id IS NOT NULL')
        )
    
    if 'ix_referentiel_is_template' not in existing_indexes:
        op.create_index('ix_referentiel_is_template', 'referentiel', ['is_template'])
    
    if 'ix_referentiel_is_active' not in existing_indexes:
        op.create_index('ix_referentiel_is_active', 'referentiel', ['is_active'])
    
    if 'ix_referentiel_tags_gin' not in existing_indexes:
        op.create_index(
            'ix_referentiel_tags_gin',
            'referentiel',
            ['tags'],
            postgresql_using='gin'
        )
    
    if 'ix_referentiel_config_gin' not in existing_indexes:
        op.create_index(
            'ix_referentiel_config_gin',
            'referentiel',
            ['config'],
            postgresql_using='gin'
        )
    
    # Migrer les données existantes
    op.execute("""
        UPDATE referentiel
        SET ref_id = 'ref-' || id::text || '-' || LOWER(REPLACE(COALESCE(nom, 'unknown'), ' ', '-'))
        WHERE ref_id IS NULL
    """)
    
    op.execute("""
        UPDATE referentiel
        SET config = metadata_json
        WHERE config IS NULL AND metadata_json IS NOT NULL
    """)
    
    op.execute("""
        UPDATE referentiel
        SET updated_at = date_import
        WHERE updated_at IS NULL AND date_import IS NOT NULL
    """)


def downgrade():
    """
    Supprimer les champs ajoutés pour le système de formulaires dynamiques.
    """
    # Supprimer les index
    op.drop_index('ix_referentiel_config_gin', table_name='referentiel')
    op.drop_index('ix_referentiel_tags_gin', table_name='referentiel')
    op.drop_index('ix_referentiel_is_active', table_name='referentiel')
    op.drop_index('ix_referentiel_is_template', table_name='referentiel')
    op.drop_index('ix_referentiel_ref_id', table_name='referentiel')
    
    # Supprimer les colonnes
    op.drop_column('referentiel', 'updated_at')
    op.drop_column('referentiel', 'source_file')
    op.drop_column('referentiel', 'is_active')
    op.drop_column('referentiel', 'is_template')
    op.drop_column('referentiel', 'tags')
    op.drop_column('referentiel', 'custom_components')
    op.drop_column('referentiel', 'custom_validators')
    op.drop_column('referentiel', 'config')
    op.drop_column('referentiel', 'ref_id')
