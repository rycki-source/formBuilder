-- ============================================================
-- FONCTIONS SQL POUR HASHER LES MOTS DE PASSE AVEC BCRYPT
-- À exécuter dans pgAdmin4
-- ============================================================

-- 1. Activer l'extension pgcrypto (si pas déjà fait)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Fonction pour hasher un mot de passe avec bcrypt
-- Utilisation: SELECT hash_password('mon_mot_de_passe');
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Génère un hash bcrypt avec un coût de 12 (même que Python bcrypt)
    RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;

-- 3. Fonction pour vérifier un mot de passe
-- Utilisation: SELECT verify_password('mon_mot_de_passe', hash_stocké);
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;

-- 4. Fonction pour mettre à jour le mot de passe d'un utilisateur
-- Utilisation: SELECT update_user_password('username', 'nouveau_mot_de_passe');
CREATE OR REPLACE FUNCTION update_user_password(
    p_username TEXT,
    p_new_password TEXT
)
RETURNS TEXT AS $$
DECLARE
    v_user_id INTEGER;
    v_new_hash TEXT;
BEGIN
    -- Vérifier que l'utilisateur existe
    SELECT id INTO v_user_id
    FROM utilisateur
    WHERE username = p_username;
    
    IF v_user_id IS NULL THEN
        RETURN 'ERREUR: Utilisateur non trouvé';
    END IF;
    
    -- Hasher le nouveau mot de passe
    v_new_hash := crypt(p_new_password, gen_salt('bf', 12));
    
    -- Mettre à jour le mot de passe
    UPDATE utilisateur
    SET mot_de_passe = v_new_hash
    WHERE id = v_user_id;
    
    RETURN 'Mot de passe mis à jour pour ' || p_username;
END;
$$ LANGUAGE plpgsql;

-- 5. Trigger pour hasher automatiquement les mots de passe lors de l'insertion
CREATE OR REPLACE FUNCTION hash_password_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Si le mot de passe ne commence pas par $2b$ (pas déjà hashé)
    IF NEW.mot_de_passe IS NOT NULL AND NOT NEW.mot_de_passe LIKE '$2b$%' THEN
        NEW.mot_de_passe := crypt(NEW.mot_de_passe, gen_salt('bf', 12));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Trigger pour hasher automatiquement lors de la mise à jour
CREATE OR REPLACE FUNCTION hash_password_on_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Si le mot de passe a changé et n'est pas déjà hashé
    IF NEW.mot_de_passe IS DISTINCT FROM OLD.mot_de_passe 
       AND NEW.mot_de_passe IS NOT NULL 
       AND NOT NEW.mot_de_passe LIKE '$2b$%' THEN
        NEW.mot_de_passe := crypt(NEW.mot_de_passe, gen_salt('bf', 12));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. Activer les triggers sur la table utilisateur
DROP TRIGGER IF EXISTS trigger_hash_password_insert ON utilisateur;
CREATE TRIGGER trigger_hash_password_insert
    BEFORE INSERT ON utilisateur
    FOR EACH ROW
    EXECUTE FUNCTION hash_password_on_insert();

DROP TRIGGER IF EXISTS trigger_hash_password_update ON utilisateur;
CREATE TRIGGER trigger_hash_password_update
    BEFORE UPDATE ON utilisateur
    FOR EACH ROW
    EXECUTE FUNCTION hash_password_on_update();

-- ============================================================
-- EXEMPLES D'UTILISATION
-- ============================================================

-- Exemple 1: Hasher un mot de passe manuellement
-- SELECT hash_password('MonMotDePasse123!');

-- Exemple 2: Créer un utilisateur (le mot de passe sera hashé automatiquement)
/*
INSERT INTO utilisateur (nom, prenom, username, email, mot_de_passe, role, statut, actif)
VALUES ('Doe', 'John', 'johndoe', 'john@example.com', 'MotDePasseClair123!', 'UTILISATEUR', 'ACTIF', true);
*/

-- Exemple 3: Mettre à jour le mot de passe d'un utilisateur
-- SELECT update_user_password('johndoe', 'NouveauMotDePasse123!');

-- Exemple 4: Mettre à jour manuellement (le trigger hashera automatiquement)
/*
UPDATE utilisateur 
SET mot_de_passe = 'NouveauMotDePasseClair123!'
WHERE username = 'johndoe';
*/

-- Exemple 5: Vérifier un mot de passe
/*
SELECT username, 
       verify_password('MotDePasseClair123!', mot_de_passe) as password_match
FROM utilisateur
WHERE username = 'johndoe';
*/

-- ============================================================
-- CORRIGER LES UTILISATEURS EXISTANTS
-- ============================================================

-- Lister tous les utilisateurs avec mot de passe non hashé
SELECT id, username, email, 
       CASE 
           WHEN mot_de_passe LIKE '$2b$%' THEN 'Hashé ✓'
           ELSE 'Non hashé ✗'
       END as statut_hash,
       LENGTH(mot_de_passe) as longueur_hash
FROM utilisateur
ORDER BY id;

-- Si vous avez des mots de passe en clair à corriger :
-- ATTENTION: Vous devez connaître les mots de passe en clair !
/*
UPDATE utilisateur SET mot_de_passe = 'MotDePasseClair' WHERE username = 'user1';
UPDATE utilisateur SET mot_de_passe = 'MotDePasseClair' WHERE username = 'user2';
-- Le trigger hashera automatiquement
*/

-- ============================================================
-- DÉSACTIVER LES TRIGGERS (si nécessaire)
-- ============================================================
/*
DROP TRIGGER IF EXISTS trigger_hash_password_insert ON utilisateur;
DROP TRIGGER IF EXISTS trigger_hash_password_update ON utilisateur;
*/
