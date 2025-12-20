"""Ajouter les tables de validation avancée

Revision ID: 003_validation_tables
Revises: 002_dynamic_forms
Create Date: 2025-12-18 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_validation_tables'
down_revision = '002_dynamic_forms'
branch_labels = None
depends_on = None


def upgrade():
    """Mettre à jour les tables de validation existantes"""
    
    # Vérifier et ajouter les colonnes manquantes à validation_soumission
    # Renommer 'valide' en 'est_valide'
    op.alter_column('validation_soumission', 'valide', new_column_name='est_valide')
    
    # Renommer 'erreurs' en 'erreurs_validation'
    op.alter_column('validation_soumission', 'erreurs', new_column_name='erreurs_validation')
    
    # Ajouter les nouvelles colonnes
    op.add_column('validation_soumission', sa.Column('score_validation', sa.Float(), nullable=True))
    op.add_column('validation_soumission', sa.Column('version_validateur', sa.String(length=50), nullable=True))
    op.add_column('validation_soumission', sa.Column('temps_validation_ms', sa.Integer(), nullable=True))
    op.add_column('validation_soumission', sa.Column('nombre_champs_valides', sa.Integer(), nullable=True))
    op.add_column('validation_soumission', sa.Column('nombre_champs_total', sa.Integer(), nullable=True))
    
    # Créer les index pour validation_soumission
    op.create_index('idx_validation_soumission_date', 'validation_soumission', ['date_validation'])
    op.create_index('idx_validation_soumission_score', 'validation_soumission', ['score_validation'])
    op.create_index('idx_validation_soumission_valide_date', 'validation_soumission', ['est_valide', 'date_validation'])
    
    # Mettre à jour rapport_validation - ajouter les nouvelles colonnes
    op.add_column('rapport_validation', sa.Column('details_validation', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.add_column('rapport_validation', sa.Column('recommandations', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('rapport_validation', sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('rapport_validation', sa.Column('champs_en_erreur', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('rapport_validation', sa.Column('champs_avec_avertissement', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('rapport_validation', sa.Column('suggestions_amelioration', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('rapport_validation', sa.Column('type_formulaire', sa.String(length=100), nullable=True))
    op.add_column('rapport_validation', sa.Column('version_template', sa.String(length=50), nullable=True))
    
    # Créer les index pour rapport_validation
    op.create_index('idx_rapport_validation_date', 'rapport_validation', ['date_creation'])
    op.create_index('idx_rapport_validation_type', 'rapport_validation', ['type_formulaire'])
    
    # Mettre à jour regle_validation_personnalisee - ajouter les nouvelles colonnes
    op.add_column('regle_validation_personnalisee', sa.Column('nombre_utilisations', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('regle_validation_personnalisee', sa.Column('derniere_utilisation', sa.DateTime(), nullable=True))
    
    # Créer les index pour regle_validation_personnalisee
    op.create_index('idx_regle_validation_formulaire_actif', 'regle_validation_personnalisee', ['formulaire_id', 'active'])
    op.create_index('idx_regle_validation_priorite', 'regle_validation_personnalisee', ['priorite'])
    
    # Mettre à jour historique_validation - ajouter les nouvelles colonnes si elles n'existent pas
    op.add_column('historique_validation', sa.Column('temps_execution_ms', sa.Integer(), nullable=True))
    op.add_column('historique_validation', sa.Column('regles_appliquees', postgresql.ARRAY(sa.String()), nullable=True))
    
    # Créer les index pour historique_validation
    op.create_index('idx_historique_validation_date', 'historique_validation', ['date_action'])
    op.create_index('idx_historique_validation_action', 'historique_validation', ['action'])


def downgrade():
    """Supprimer les tables de validation avancée"""
    op.drop_table('historique_validation')
    op.drop_table('regle_validation_personnalisee')
    op.drop_table('rapport_validation')
    op.drop_table('validation_soumission')