"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial database schema"""
    
    # Table utilisateur
    op.create_table(
        'utilisateur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('prenom', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('mot_de_passe', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('actif', sa.Boolean(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utilisateur_email'), 'utilisateur', ['email'], unique=True)
    op.create_index(op.f('ix_utilisateur_id'), 'utilisateur', ['id'], unique=False)

    # Table referentiel
    op.create_table(
        'referentiel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('valide', sa.Boolean(), nullable=True),
        sa.Column('personne_import_id', sa.Integer(), nullable=True),
        sa.Column('date_import', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['personne_import_id'], ['utilisateur.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referentiel_id'), 'referentiel', ['id'], unique=False)
    op.create_index(op.f('ix_referentiel_nom'), 'referentiel', ['nom'], unique=True)

    # Table formulaire
    op.create_table(
        'formulaire',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referentiel_id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type_formulaire', sa.String(length=50), nullable=False),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('date_creation', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_modification', sa.DateTime(), nullable=True),
        sa.Column('createur_id', sa.Integer(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['createur_id'], ['utilisateur.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['referentiel_id'], ['referentiel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formulaire_id'), 'formulaire', ['id'], unique=False)

    # Table soumission
    op.create_table(
        'soumission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('formulaire_id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.Column('donnees_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('date_soumission', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_modification', sa.DateTime(), nullable=True),
        sa.Column('ip_adresse', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['formulaire_id'], ['formulaire.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_soumission_id'), 'soumission', ['id'], unique=False)

    # Table connexion_bdd_externe
    op.create_table(
        'connexion_bdd_externe',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referentiel_id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('type_bdd', sa.String(length=50), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('nom_bdd', sa.String(length=255), nullable=False),
        sa.Column('utilisateur', sa.String(length=255), nullable=False),
        sa.Column('mot_de_passe', sa.String(length=255), nullable=False),
        sa.Column('schema_string', sa.String(length=100), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['referentiel_id'], ['referentiel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Table referentiel_donnees
    op.create_table(
        'referentiel_donnees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referentiel_id', sa.Integer(), nullable=False),
        sa.Column('cle', sa.String(length=255), nullable=False),
        sa.Column('valeur', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True),
        sa.Column('ordre', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['referentiel_id'], ['referentiel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Table audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entite_type', sa.String(length=50), nullable=True),
        sa.Column('entite_id', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_adresse', sa.String(length=45), nullable=True),
        sa.Column('date_action', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_id'), 'audit_log', ['id'], unique=False)

    # Table consentement_rgpd
    op.create_table(
        'consentement_rgpd',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.Column('type_consentement', sa.String(length=100), nullable=False),
        sa.Column('accepte', sa.Boolean(), nullable=False),
        sa.Column('date_consentement', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('ip_adresse', sa.String(length=45), nullable=True),
        sa.Column('preuve', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Drop all tables"""
    op.drop_table('consentement_rgpd')
    op.drop_index(op.f('ix_audit_log_id'), table_name='audit_log')
    op.drop_table('audit_log')
    op.drop_table('referentiel_donnees')
    op.drop_table('connexion_bdd_externe')
    op.drop_index(op.f('ix_soumission_id'), table_name='soumission')
    op.drop_table('soumission')
    op.drop_index(op.f('ix_formulaire_id'), table_name='formulaire')
    op.drop_table('formulaire')
    op.drop_index(op.f('ix_referentiel_nom'), table_name='referentiel')
    op.drop_index(op.f('ix_referentiel_id'), table_name='referentiel')
    op.drop_table('referentiel')
    op.drop_index(op.f('ix_utilisateur_id'), table_name='utilisateur')
    op.drop_index(op.f('ix_utilisateur_email'), table_name='utilisateur')
    op.drop_table('utilisateur')
