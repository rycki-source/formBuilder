"""
Script pour installer les fonctions SQL de hashage bcrypt dans PostgreSQL
"""
import asyncio
from sqlalchemy import text
from app.db.session import engine


async def install_sql_functions():
    """Installer les fonctions SQL depuis le fichier"""
    
    print("\n🔧 Installation des fonctions SQL de hashage bcrypt...")
    
    # Lire le fichier SQL
    with open('sql_functions_bcrypt.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Séparer les commandes SQL
    # On exécute par blocs pour éviter les erreurs
    sql_blocks = [
        # Extension pgcrypto
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
        
        # Fonction hash_password
        """
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;
        """,
        
        # Fonction verify_password
        """
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;
        """,
        
        # Fonction update_user_password
        """
CREATE OR REPLACE FUNCTION update_user_password(
    p_username TEXT,
    p_new_password TEXT
)
RETURNS TEXT AS $$
DECLARE
    v_user_id INTEGER;
    v_new_hash TEXT;
BEGIN
    SELECT id INTO v_user_id
    FROM utilisateur
    WHERE username = p_username;
    
    IF v_user_id IS NULL THEN
        RETURN 'ERREUR: Utilisateur non trouvé';
    END IF;
    
    v_new_hash := crypt(p_new_password, gen_salt('bf', 12));
    
    UPDATE utilisateur
    SET mot_de_passe = v_new_hash
    WHERE id = v_user_id;
    
    RETURN 'Mot de passe mis à jour pour ' || p_username;
END;
$$ LANGUAGE plpgsql;
        """,
        
        # Fonction trigger insert
        """
CREATE OR REPLACE FUNCTION hash_password_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mot_de_passe IS NOT NULL AND NOT NEW.mot_de_passe LIKE '$2b$%' THEN
        NEW.mot_de_passe := crypt(NEW.mot_de_passe, gen_salt('bf', 12));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
        """,
        
        # Fonction trigger update
        """
CREATE OR REPLACE FUNCTION hash_password_on_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mot_de_passe IS DISTINCT FROM OLD.mot_de_passe 
       AND NEW.mot_de_passe IS NOT NULL 
       AND NOT NEW.mot_de_passe LIKE '$2b$%' THEN
        NEW.mot_de_passe := crypt(NEW.mot_de_passe, gen_salt('bf', 12));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
        """,
        
        # Triggers
        "DROP TRIGGER IF EXISTS trigger_hash_password_insert ON utilisateur;",
        """
CREATE TRIGGER trigger_hash_password_insert
    BEFORE INSERT ON utilisateur
    FOR EACH ROW
    EXECUTE FUNCTION hash_password_on_insert();
        """,
        
        "DROP TRIGGER IF EXISTS trigger_hash_password_update ON utilisateur;",
        """
CREATE TRIGGER trigger_hash_password_update
    BEFORE UPDATE ON utilisateur
    FOR EACH ROW
    EXECUTE FUNCTION hash_password_on_update();
        """
    ]
    
    async with engine.begin() as conn:
        try:
            for i, sql_block in enumerate(sql_blocks, 1):
                sql_block = sql_block.strip()
                if sql_block:
                    print(f"  [{i}/{len(sql_blocks)}] Exécution...")
                    await conn.execute(text(sql_block))
            
            print("\n✅ Toutes les fonctions SQL ont été installées avec succès!")
            print("\n📋 Fonctions disponibles:")
            print("  - hash_password(password) : Hasher un mot de passe")
            print("  - verify_password(password, hash) : Vérifier un mot de passe")
            print("  - update_user_password(username, new_password) : Mettre à jour un mot de passe")
            print("  - Triggers automatiques sur INSERT/UPDATE")
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'installation: {e}")
            import traceback
            traceback.print_exc()
            raise


async def test_functions():
    """Tester les fonctions installées"""
    print("\n🧪 Test des fonctions...")
    
    async with engine.begin() as conn:
        # Test 1: Hasher un mot de passe
        result = await conn.execute(
            text("SELECT hash_password(:pwd) as hash"),
            {"pwd": "TestPassword123!"}
        )
        row = result.fetchone()
        if row is None:
            print("❌ Erreur: Impossible de hasher le mot de passe")
            return
        test_hash = row[0]
        print(f"\n  Test hash: {test_hash[:50]}...")
        
        # Test 2: Vérifier le mot de passe
        result = await conn.execute(
            text("SELECT verify_password(:pwd, :hash) as valid"),
            {"pwd": "TestPassword123!", "hash": test_hash}
        )
        row = result.fetchone()
        if row is None:
            print("❌ Erreur: Impossible de vérifier le mot de passe")
            return
        is_valid = row[0]
        print(f"  Vérification: {'✅ OK' if is_valid else '❌ ERREUR'}")
        
        # Test 3: Lister les utilisateurs et leur statut de hash
        result = await conn.execute(
            text("""
                SELECT username, 
                       CASE 
                           WHEN mot_de_passe LIKE '$2b$%' THEN 'Hashé ✓'
                           ELSE 'Non hashé ✗'
                       END as statut
                FROM utilisateur
                ORDER BY id
            """)
        )
        
        print("\n  État des mots de passe des utilisateurs:")
        for row in result:
            print(f"    - {row[0]}: {row[1]}")


if __name__ == "__main__":
    asyncio.run(install_sql_functions())
    asyncio.run(test_functions())
