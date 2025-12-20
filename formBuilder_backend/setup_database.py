"""
Script de mise en place complète de la base de données FormBuilder
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

async def setup_database():
    """Mise en place complète de la base de données"""
    
    print("🚀 MISE EN PLACE DE LA BASE DE DONNÉES FORMBUILDER")
    print("=" * 60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    try:
        # 1. Vérifier la connexion
        print("\n1️⃣ Vérification de la connexion...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            version_str = version.split(',')[0] if version else "Version inconnue"
            print(f"   ✅ PostgreSQL connecté: {version_str}")
        
        # 2. Créer les tables si elles n'existent pas
        print("\n2️⃣ Création/Vérification des tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("   ✅ Toutes les tables sont créées/vérifiées")
        
        # 3. Vérifier les tables existantes
        print("\n3️⃣ Inventaire des tables...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"   📊 {len(tables)} tables trouvées:")
            for i, table in enumerate(tables, 1):
                print(f"      {i:2d}. {table}")
        
        # 4. Vérifier/Créer les données initiales
        print("\n4️⃣ Vérification des données initiales...")
        
        from sqlalchemy.ext.asyncio import async_sessionmaker
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            # Vérifier les utilisateurs existants
            result = await session.execute(text("SELECT COUNT(*) FROM utilisateur"))
            user_count = result.scalar()
            print(f"   👥 Utilisateurs existants: {user_count}")
            
            if user_count == 0:
                print("   🔧 Création de l'utilisateur administrateur...")
                
                # Insérer directement en SQL pour éviter les dépendances complexes
                admin_password_hash = hash_password("admin")
                
                await session.execute(text("""
                    INSERT INTO utilisateur (email, username, mot_de_passe_hash, role, actif, date_creation)
                    VALUES (:email, :username, :password_hash, :role, :actif, NOW())
                """), {
                    "email": "admin@admin.com",
                    "username": "admin",
                    "password_hash": admin_password_hash,
                    "role": "ADMIN",
                    "actif": True
                })
                
                await session.commit()
                print("   ✅ Administrateur créé: admin@admin.com / admin")
            
            # Vérifier les formulaires
            result = await session.execute(text("SELECT COUNT(*) FROM formulaire"))
            form_count = result.scalar()
            print(f"   📋 Formulaires existants: {form_count}")
            
            # Vérifier les référentiels
            result = await session.execute(text("SELECT COUNT(*) FROM referentiel"))
            ref_count = result.scalar()
            print(f"   📚 Référentiels existants: {ref_count}")
        
        # 5. Test final de l'application
        print("\n5️⃣ Test final de la configuration...")
        
        # Simuler le démarrage de l'app pour vérifier les imports
        try:
            from app.main import app
            print("   ✅ Application FastAPI chargée avec succès")
        except Exception as e:
            print(f"   ⚠️  Avertissement lors du chargement de l'app: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 BASE DE DONNÉES CONFIGURÉE AVEC SUCCÈS !")
        print("=" * 60)
        print("\n📋 Résumé de la configuration:")
        print(f"   • Base de données: formbuilder")
        print(f"   • Tables: {len(tables)}")
        print(f"   • Utilisateurs: {user_count if user_count and user_count > 0 else 1}")
        print(f"   • Formulaires: {form_count}")
        print(f"   • Référentiels: {ref_count}")
        
        print(f"\n🔐 Connexion administrateur:")
        print(f"   Email: admin@admin.com")
        print(f"   Mot de passe: admin")
        
        print(f"\n🚀 Pour démarrer l'application:")
        print(f"   cd formBuilder_backend")
        print(f"   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la mise en place: {e}")
        print(f"\n🔧 Actions recommandées:")
        print(f"   1. Vérifiez que PostgreSQL est démarré")
        print(f"   2. Vérifiez les paramètres dans .env")
        print(f"   3. Créez la base 'formbuilder' si elle n'existe pas:")
        print(f"      createdb -U postgres formbuilder")
        return False
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(setup_database())