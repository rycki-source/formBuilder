-- =====================================================
-- FormBuilder Database Schema Export
-- Generated: 2025-12-12 10:04:27
-- =====================================================


-- =====================================================
-- TABLES
-- =====================================================


-- Table: admin_alert
CREATE TABLE IF NOT EXISTS admin_alert (
  id INTEGER NOT NULL DEFAULT nextval('admin_alert_id_seq'::regclass),
  titre VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  statut TEXT NOT NULL,
  type_alert TEXT NOT NULL,
  lu BOOLEAN DEFAULT false,
  persistant BOOLEAN DEFAULT true,
  utilisateur_id INTEGER,
  formulaire_id INTEGER,
  metadata_json TEXT,
  date_creation TIMESTAMP DEFAULT now(),
  date_lecture TIMESTAMP,
  date_expiration TIMESTAMP,
  PRIMARY KEY (id)
);


-- Table: admin_audit
CREATE TABLE IF NOT EXISTS admin_audit (
  id INTEGER NOT NULL DEFAULT nextval('admin_audit_id_seq'::regclass),
  user_id INTEGER,
  username VARCHAR(255) NOT NULL,
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id INTEGER,
  description TEXT NOT NULL,
  changes_json TEXT,
  ip_address VARCHAR(45),
  user_agent VARCHAR(500),
  endpoint VARCHAR(255),
  success INTEGER,
  error_message TEXT,
  date_action TIMESTAMP WITH TIME ZONE DEFAULT now(),
  PRIMARY KEY (id),

);


-- Table: alembic_version
CREATE TABLE IF NOT EXISTS alembic_version (
  version_num VARCHAR(32) NOT NULL,
  PRIMARY KEY (version_num)
);


-- Table: alert
CREATE TABLE IF NOT EXISTS alert (
  id INTEGER NOT NULL DEFAULT nextval('alert_id_seq'::regclass),
  titre VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  metadata_json TEXT,
  source VARCHAR(100),
  user_id INTEGER,
  lu BOOLEAN,
  persistent BOOLEAN,
  archive BOOLEAN,
  date_creation TIMESTAMP WITH TIME ZONE DEFAULT now(),
  date_lecture TIMESTAMP WITH TIME ZONE,
  date_expiration TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
);


-- Table: audit_log
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER NOT NULL DEFAULT nextval('audit_log_id_seq'::regclass),
  utilisateur_id INTEGER,
  action VARCHAR(100) NOT NULL,
  entite_type VARCHAR(50),
  entite_id INTEGER,
  details JSONB,
  ip_adresse VARCHAR(45),
  date_action TIMESTAMP DEFAULT now(),
  PRIMARY KEY (id),

);


-- Table: champ
CREATE TABLE IF NOT EXISTS champ (
  id INTEGER NOT NULL DEFAULT nextval('champ_id_seq'::regclass),
  formulaire_id INTEGER NOT NULL,
  nom VARCHAR(255) NOT NULL,
  label VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,
  obligatoire BOOLEAN,
  valeur_par_defaut JSONB,
  visible BOOLEAN,
  ordre INTEGER NOT NULL,
  config_json JSONB,
  PRIMARY KEY (id),

);


-- Table: connexion_bdd_externe
CREATE TABLE IF NOT EXISTS connexion_bdd_externe (
  id INTEGER NOT NULL DEFAULT nextval('connexion_bdd_externe_id_seq'::regclass),
  referentiel_id INTEGER NOT NULL,
  nom VARCHAR(255) NOT NULL,
  type_bdd VARCHAR(50) NOT NULL,
  host VARCHAR(255) NOT NULL,
  port INTEGER NOT NULL,
  nom_bdd VARCHAR(255) NOT NULL,
  utilisateur VARCHAR(255) NOT NULL,
  mot_de_passe VARCHAR(255) NOT NULL,
  schema_string VARCHAR(100),
  actif BOOLEAN,
  date_creation TIMESTAMP DEFAULT now(),
  PRIMARY KEY (id),

);


-- Table: consentement_rgpd
CREATE TABLE IF NOT EXISTS consentement_rgpd (
  id INTEGER NOT NULL DEFAULT nextval('consentement_rgpd_id_seq'::regclass),
  utilisateur_id INTEGER,
  type_consentement VARCHAR(100) NOT NULL,
  accepte BOOLEAN NOT NULL,
  date_consentement TIMESTAMP DEFAULT now(),
  ip_adresse VARCHAR(45),
  preuve TEXT,
  PRIMARY KEY (id),

);


-- Table: demande_suppression
CREATE TABLE IF NOT EXISTS demande_suppression (
  id INTEGER NOT NULL DEFAULT nextval('demande_suppression_id_seq'::regclass),
  utilisateur_id INTEGER,
  soumission_id INTEGER,
  raison TEXT,
  statut VARCHAR(20),
  date_demande TIMESTAMP DEFAULT now(),
  date_execution TIMESTAMP,
  PRIMARY KEY (id),

);


-- Table: error_log
CREATE TABLE IF NOT EXISTS error_log (
  id INTEGER NOT NULL DEFAULT nextval('error_log_id_seq'::regclass),
  type_erreur TEXT NOT NULL,
  severite TEXT NOT NULL,
  message TEXT NOT NULL,
  stack_trace TEXT,
  endpoint VARCHAR(255),
  methode_http VARCHAR(10),
  user_id INTEGER,
  ip_address VARCHAR(45),
  user_agent VARCHAR(500),
  metadata_json TEXT,
  request_data TEXT,
  resolu INTEGER,
  notes TEXT,
  date_erreur TIMESTAMP WITH TIME ZONE DEFAULT now(),
  date_resolution TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
);


-- Table: fichier_joint
CREATE TABLE IF NOT EXISTS fichier_joint (
  id INTEGER NOT NULL DEFAULT nextval('fichier_joint_id_seq'::regclass),
  soumission_id INTEGER NOT NULL,
  nom_original VARCHAR(255) NOT NULL,
  nom_stockage VARCHAR(255) NOT NULL,
  format VARCHAR(50) NOT NULL,
  chemin_s3 TEXT NOT NULL,
  taille_bytes BIGINT NOT NULL,
  mime_type VARCHAR(100),
  date_upload TIMESTAMP DEFAULT now(),
  PRIMARY KEY (id),

);


-- Table: formulaire
CREATE TABLE IF NOT EXISTS formulaire (
  id INTEGER NOT NULL DEFAULT nextval('formulaire_id_seq'::regclass),
  referentiel_id INTEGER,
  nom VARCHAR(255) NOT NULL,
  description TEXT,
  type_formulaire VARCHAR(50),
  statut VARCHAR(50),
  version VARCHAR(20),
  date_creation TIMESTAMP DEFAULT now(),
  date_modification TIMESTAMP NOT NULL,
  createur_id INTEGER,
  actif BOOLEAN,
  developpeur_id INTEGER,
  type_structurel VARCHAR(50) NOT NULL DEFAULT 'simple'::character varying,
  type_fonctionnel VARCHAR(50) NOT NULL DEFAULT 'personnalise'::character varying,
  structure_json JSONB NOT NULL,
  publie BOOLEAN DEFAULT false,
  webhook_url VARCHAR(500),
  webhook_enabled BOOLEAN DEFAULT false,
  webhook_secret VARCHAR(255),
  webhook_retry_count INTEGER DEFAULT 3,
  PRIMARY KEY (id),

);


-- Table: formulaire_version
CREATE TABLE IF NOT EXISTS formulaire_version (
  id INTEGER NOT NULL DEFAULT nextval('formulaire_version_id_seq'::regclass),
  formulaire_id INTEGER NOT NULL,
  numero_version VARCHAR(20) NOT NULL,
  majeur INTEGER NOT NULL,
  mineur INTEGER NOT NULL,
  patch INTEGER NOT NULL,
  structure_json JSONB NOT NULL,
  commentaire TEXT,
  date_creation TIMESTAMP DEFAULT now(),
  auteur_id INTEGER,
  actif BOOLEAN,
  PRIMARY KEY (id),

);


-- Table: permission
CREATE TABLE IF NOT EXISTS permission (
  id INTEGER NOT NULL DEFAULT nextval('permission_id_seq'::regclass),
  code VARCHAR(100) NOT NULL,
  nom VARCHAR(255) NOT NULL,
  description TEXT,
  categorie VARCHAR(50),
  date_creation TIMESTAMP WITH TIME ZONE DEFAULT now(),
  PRIMARY KEY (id)
);


-- Table: rapport_validation
CREATE TABLE IF NOT EXISTS rapport_validation (
  id INTEGER NOT NULL DEFAULT nextval('rapport_validation_id_seq'::regclass),
  soumission_id INTEGER NOT NULL,
  erreurs JSONB,
  avertissements JSONB,
  resume_texte TEXT,
  date_generation TIMESTAMP DEFAULT now(),
  PRIMARY KEY (id),

);


-- Table: referentiel
CREATE TABLE IF NOT EXISTS referentiel (
  id INTEGER NOT NULL DEFAULT nextval('referentiel_id_seq'::regclass),
  nom VARCHAR(255) NOT NULL,
  description TEXT,
  version VARCHAR(20),
  source_type VARCHAR(20) NOT NULL,
  metadata_json JSONB,
  valide BOOLEAN,
  personne_import_id INTEGER,
  date_import TIMESTAMP DEFAULT now(),
  ref_id VARCHAR(100),
  config JSONB,
  custom_validators JSONB,
  custom_components JSONB,
  tags JSONB,
  is_template BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  source_file VARCHAR(255),
  updated_at TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id),

);


-- Table: referentiel_donnees
CREATE TABLE IF NOT EXISTS referentiel_donnees (
  id INTEGER NOT NULL DEFAULT nextval('referentiel_donnees_id_seq'::regclass),
  referentiel_id INTEGER NOT NULL,
  cle VARCHAR(255) NOT NULL,
  valeur TEXT NOT NULL,
  description TEXT,
  actif BOOLEAN,
  ordre INTEGER,
  PRIMARY KEY (id),

);


-- Table: regle_validation
CREATE TABLE IF NOT EXISTS regle_validation (
  id INTEGER NOT NULL DEFAULT nextval('regle_validation_id_seq'::regclass),
  champ_id INTEGER NOT NULL,
  type VARCHAR(100) NOT NULL,
  expression TEXT,
  message_erreur VARCHAR(255) NOT NULL,
  dependance_champ_id INTEGER,
  PRIMARY KEY (id),

);


-- Table: role
CREATE TABLE IF NOT EXISTS role (
  id INTEGER NOT NULL DEFAULT nextval('role_id_seq'::regclass),
  code VARCHAR(50) NOT NULL,
  nom VARCHAR(255) NOT NULL,
  description TEXT,
  is_system BOOLEAN,
  actif BOOLEAN,
  date_creation TIMESTAMP WITH TIME ZONE DEFAULT now(),
  date_modification TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
);


-- Table: role_permission
CREATE TABLE IF NOT EXISTS role_permission (
  role_id INTEGER NOT NULL,
  permission_id INTEGER NOT NULL,
  PRIMARY KEY (role_id, permission_id),

);


-- Table: soumission
CREATE TABLE IF NOT EXISTS soumission (
  id INTEGER NOT NULL DEFAULT nextval('soumission_id_seq'::regclass),
  formulaire_id INTEGER NOT NULL,
  utilisateur_id INTEGER,
  donnees_json JSONB NOT NULL,
  statut VARCHAR(50),
  date_soumission TIMESTAMP DEFAULT now(),
  date_modification TIMESTAMP,
  ip_adresse VARCHAR(45),
  user_agent VARCHAR(255),
  PRIMARY KEY (id),

);


-- Table: user_role
CREATE TABLE IF NOT EXISTS user_role (
  user_id INTEGER NOT NULL,
  role_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, role_id),

);


-- Table: utilisateur
CREATE TABLE IF NOT EXISTS utilisateur (
  id INTEGER NOT NULL DEFAULT nextval('utilisateur_id_seq'::regclass),
  nom VARCHAR(255) NOT NULL,
  prenom VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  mot_de_passe VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  actif BOOLEAN,
  date_creation TIMESTAMP DEFAULT now(),
  username VARCHAR(255) NOT NULL,
  statut VARCHAR(20) DEFAULT 'ACTIF'::character varying,
  derniere_connexion TIMESTAMP,
  modifier_profil BOOLEAN DEFAULT true,
  verifier_permission BOOLEAN DEFAULT true,
  PRIMARY KEY (id)
);


-- Table: validation_soumission
CREATE TABLE IF NOT EXISTS validation_soumission (
  id INTEGER NOT NULL DEFAULT nextval('validation_soumission_id_seq'::regclass),
  soumission_id INTEGER NOT NULL,
  regles_appliquees JSONB NOT NULL,
  erreurs JSONB,
  avertissements JSONB,
  valide BOOLEAN,
  date_validation TIMESTAMP DEFAULT now(),
  PRIMARY KEY (id),

);


-- =====================================================
-- INDEXES
-- =====================================================

-- Index on admin_alert
CREATE INDEX ix_admin_alert_date_creation ON public.admin_alert USING btree (date_creation);

-- Index on admin_alert
CREATE INDEX ix_admin_alert_id ON public.admin_alert USING btree (id);

-- Index on admin_audit
CREATE INDEX ix_admin_audit_action ON public.admin_audit USING btree (action);

-- Index on admin_audit
CREATE INDEX ix_admin_audit_date_action ON public.admin_audit USING btree (date_action);

-- Index on admin_audit
CREATE INDEX ix_admin_audit_id ON public.admin_audit USING btree (id);

-- Index on alembic_version
CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num);

-- Index on alert
CREATE INDEX ix_alert_id ON public.alert USING btree (id);

-- Index on audit_log
CREATE INDEX ix_audit_log_id ON public.audit_log USING btree (id);

-- Index on champ
CREATE INDEX ix_champ_formulaire_id ON public.champ USING btree (formulaire_id);

-- Index on champ
CREATE INDEX ix_champ_id ON public.champ USING btree (id);

-- Index on demande_suppression
CREATE INDEX ix_demande_suppression_id ON public.demande_suppression USING btree (id);

-- Index on error_log
CREATE INDEX ix_error_log_date_erreur ON public.error_log USING btree (date_erreur);

-- Index on error_log
CREATE INDEX ix_error_log_id ON public.error_log USING btree (id);

-- Index on fichier_joint
CREATE INDEX ix_fichier_joint_id ON public.fichier_joint USING btree (id);

-- Index on fichier_joint
CREATE INDEX ix_fichier_joint_soumission_id ON public.fichier_joint USING btree (soumission_id);

-- Index on formulaire
CREATE INDEX ix_formulaire_actif ON public.formulaire USING btree (actif);

-- Index on formulaire
CREATE INDEX ix_formulaire_developpeur_id ON public.formulaire USING btree (developpeur_id);

-- Index on formulaire
CREATE INDEX ix_formulaire_id ON public.formulaire USING btree (id);

-- Index on formulaire
CREATE INDEX ix_formulaire_nom ON public.formulaire USING btree (nom);

-- Index on formulaire
CREATE INDEX ix_formulaire_publie ON public.formulaire USING btree (publie);

-- Index on formulaire_version
CREATE UNIQUE INDEX formulaire_version_formulaire_id_numero_version_key ON public.formulaire_version USING btree (formulaire_id, numero_version);

-- Index on formulaire_version
CREATE INDEX ix_formulaire_version_id ON public.formulaire_version USING btree (id);

-- Index on permission
CREATE UNIQUE INDEX ix_permission_code ON public.permission USING btree (code);

-- Index on permission
CREATE INDEX ix_permission_id ON public.permission USING btree (id);

-- Index on rapport_validation
CREATE INDEX ix_rapport_validation_id ON public.rapport_validation USING btree (id);

-- Index on referentiel
CREATE INDEX ix_referentiel_config_gin ON public.referentiel USING gin (config);

-- Index on referentiel
CREATE INDEX ix_referentiel_id ON public.referentiel USING btree (id);

-- Index on referentiel
CREATE INDEX ix_referentiel_is_active ON public.referentiel USING btree (is_active);

-- Index on referentiel
CREATE INDEX ix_referentiel_is_template ON public.referentiel USING btree (is_template);

-- Index on referentiel
CREATE UNIQUE INDEX ix_referentiel_nom ON public.referentiel USING btree (nom);

-- Index on referentiel
CREATE UNIQUE INDEX ix_referentiel_ref_id ON public.referentiel USING btree (ref_id) WHERE (ref_id IS NOT NULL);

-- Index on referentiel
CREATE INDEX ix_referentiel_tags_gin ON public.referentiel USING gin (tags);

-- Index on regle_validation
CREATE INDEX ix_regle_validation_champ_id ON public.regle_validation USING btree (champ_id);

-- Index on regle_validation
CREATE INDEX ix_regle_validation_id ON public.regle_validation USING btree (id);

-- Index on role
CREATE UNIQUE INDEX ix_role_code ON public.role USING btree (code);

-- Index on role
CREATE INDEX ix_role_id ON public.role USING btree (id);

-- Index on soumission
CREATE INDEX ix_soumission_id ON public.soumission USING btree (id);

-- Index on utilisateur
CREATE UNIQUE INDEX ix_utilisateur_email ON public.utilisateur USING btree (email);

-- Index on utilisateur
CREATE INDEX ix_utilisateur_id ON public.utilisateur USING btree (id);

-- Index on utilisateur
CREATE UNIQUE INDEX ix_utilisateur_username ON public.utilisateur USING btree (username);

-- Index on validation_soumission
CREATE INDEX ix_validation_soumission_id ON public.validation_soumission USING btree (id);

-- Index on validation_soumission
CREATE UNIQUE INDEX validation_soumission_soumission_id_key ON public.validation_soumission USING btree (soumission_id);


-- =====================================================
-- DATA STATISTICS
-- =====================================================

-- admin_alert: 0 rows
-- admin_audit: 0 rows
-- alembic_version: 1 rows
-- alert: 0 rows
-- audit_log: 21 rows
-- champ: 0 rows
-- connexion_bdd_externe: 0 rows
-- consentement_rgpd: 0 rows
-- demande_suppression: 0 rows
-- error_log: 0 rows
-- fichier_joint: 0 rows
-- formulaire: 30 rows
-- formulaire_version: 29 rows
-- permission: 0 rows
-- rapport_validation: 0 rows
-- referentiel: 32 rows
-- referentiel_donnees: 0 rows
-- regle_validation: 0 rows
-- role: 0 rows
-- role_permission: 0 rows
-- soumission: 6 rows
-- user_role: 0 rows
-- utilisateur: 1 rows
-- validation_soumission: 0 rows


-- =====================================================
-- SAMPLE DATA (Admin User)
-- =====================================================

