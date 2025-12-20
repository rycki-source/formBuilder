"""
Script de test de connexion à la base de données
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire app au path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def test_database_connection():
    """Test de connexion à PostgreSQL"""
    
    print("🔍 Test de connexion à la base de données...")
    print(f"📊 URL: {settings.DATABASE_URL}")
    
    try:
        # Créer le moteur de base de données
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        # Test de connexion
        async with engine.connect() as conn:
            # Test simple
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connexion réussie !")
            print(f"📋 Version PostgreSQL: {version}")
            
            # Test des tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"📚 Nombre de tables: {len(tables)}")
            
            # Test des données
            stats = {}
            for table in tables[:10]:  # Limiter à 10 tables pour l'affichage
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    stats[table] = count
                except Exception as e:
                    stats[table] = f"Erreur: {str(e)}"
            
            print(f"\n📊 Statistiques des principales tables:")
            for table, count in stats.items():
                print(f"  - {table}: {count} lignes")
            
            # Test d'authentification avec un utilisateur
            try:
                result = await conn.execute(text("""
                    SELECT username, email, role, actif 
                    FROM "user" 
                    WHERE actif = true 
                    LIMIT 3
                """))
                users = result.fetchall()
                
                print(f"\n👥 Utilisateurs actifs ({len(users)}):")
                for user in users:
                    print(f"  - {user[0]} ({user[1]}) - {user[2]}")
                    
            except Exception as e:
                print(f"⚠️  Erreur lors de la lecture des utilisateurs: {e}")
        
        await engine.dispose()
        print(f"\n✅ Tous les tests de connexion sont passés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print(f"\n🔧 Vérifications à effectuer:")
        print(f"  1. PostgreSQL est-il démarré ?")
        print(f"  2. La base 'formbuilder' existe-t-elle ?")
        print(f"  3. L'utilisateur 'fb_user' a-t-il les permissions ?")
        print(f"  4. Le mot de passe est-il correct ?")
        
        # Suggestions de commandes
        print(f"\n💡 Commandes utiles:")
        print(f"  psql -h localhost -U fb_user -d formbuilder")
        print(f"  pg_isready -h localhost -p 5432")
        
        return False
    
    return True

async def test_redis_connection():
    """Test de connexion à Redis"""
    print(f"\n🔍 Test de connexion à Redis...")
    print(f"📊 URL: {settings.REDIS_URL}")
    
    try:
        import redis.asyncio as redis
        
        # Extraire l'URL Redis
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Test ping
        pong = await redis_client.ping()
        print(f"✅ Redis connexion réussie: {pong}")
        
        # Test set/get
        await redis_client.set("test_key", "test_value", ex=10)
        value = await redis_client.get("test_key")
        print(f"✅ Test lecture/écriture: {value}")
        
        await redis_client.close()
        
    except ImportError:
        print(f"⚠️  Redis client non installé (optionnel)")
        print(f"   pip install redis[hiredis]")
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        print(f"💡 Commande pour démarrer Redis: redis-server")

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("🧪 TEST DE CONNEXION - FORMBUILDER DATABASE")
        print("=" * 60)
        
        # Test PostgreSQL
        db_ok = await test_database_connection()
        
        # Test Redis
        await test_redis_connection()
        
        print("\n" + "=" * 60)
        if db_ok:
            print("🎉 Configuration de base de données validée !")
        else:
            print("⚠️  Problèmes de configuration détectés")
        print("=" * 60)
    
    asyncio.run(main())