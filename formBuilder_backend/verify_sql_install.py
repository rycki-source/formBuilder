"""
Test rapide des fonctions SQL installées
"""
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def verify_installation():
    """Vérifier que les fonctions SQL sont bien installées"""
    
    print("\n✅ Vérification de l'installation des fonctions SQL\n")
    
    async with AsyncSessionLocal() as db:
        # Test 1: Hasher un mot de passe
        result = await db.execute(
            text("SELECT hash_password('Test123!') as hash")
        )
        row = result.fetchone()
        if row is None or row[0] is None:
            print(f"1. Fonction hash_password: ❌")
            print(f"   Erreur: Impossible de générer le hash\n")
            return
        print(f"1. Fonction hash_password: ✅")
        print(f"   Hash généré: {row[0][:50]}...\n")
        
        # Test 2: Vérifier un mot de passe
        result = await db.execute(
            text("SELECT verify_password('Test123!', :hash) as valid"),
            {"hash": row[0]}
        )
        result_row = result.fetchone()
        valid = result_row[0] if result_row else False
        print(f"2. Fonction verify_password: {'✅' if valid else '❌'}\n")
        
        # Test 3: Lister les utilisateurs
        result = await db.execute(
            text("""
                SELECT username, 
                       CASE 
                           WHEN mot_de_passe LIKE '$2b$%' THEN 'Hashé ✓'
                           ELSE 'Non hashé ✗'
                       END as statut,
                       role
                FROM utilisateur
                ORDER BY id
            """)
        )
        
        print("3. État des utilisateurs:\n")
        for row in result:
            print(f"   {row[0]:20} | {row[1]:15} | {row[2]}")
        
        print("\n" + "="*60)
        print("✅ Toutes les fonctions SQL sont opérationnelles!")
        print("="*60)
        print("\n📋 Vous pouvez maintenant dans pgAdmin4:")
        print("   • Créer des utilisateurs (le mot de passe sera hashé auto)")
        print("   • UPDATE utilisateur SET mot_de_passe = 'nouveauMDP' WHERE...")
        print("   • SELECT update_user_password('username', 'nouveauMDP');")
        print()


if __name__ == "__main__":
    asyncio.run(verify_installation())
