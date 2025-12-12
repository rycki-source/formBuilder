"""Test pour vérifier ce qui est stocké en base de données"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models.referentiel import Referentiel
from app.core.config import settings
import json

async def check_referentiel():
    """Vérifier le dernier référentiel créé"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(
        engine, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        # Récupérer le dernier référentiel
        result = await session.execute(
            select(Referentiel).order_by(Referentiel.id.desc()).limit(1)
        )
        ref = result.scalar_one_or_none()
        
        if not ref:
            print("❌ Aucun référentiel trouvé en base")
            return
        
        print(f"\n🔍 Référentiel ID: {ref.id}")
        print(f"📝 Nom: {ref.nom}")
        print(f"📦 Source: {ref.source_type}")
        print(f"✅ Valide: {ref.valide}")
        print(f"\n📊 metadata_json:")
        print(json.dumps(ref.metadata_json, indent=2, ensure_ascii=False))
        
        # Vérifier si config existe dans metadata_json
        metadata = ref.metadata_json if ref.metadata_json is not None else {}
        if isinstance(metadata, dict) and 'config' in metadata:
            config = metadata['config']
            print(f"\n✅ Config trouvé dans metadata_json")
            print(f"📋 Sections: {len(config.get('sections', []))}")
            
            for i, section in enumerate(config.get('sections', [])):
                print(f"\n  Section {i+1}: {section.get('title')}")
                print(f"    ID: {section.get('id')}")
                print(f"    Groupes: {len(section.get('groups', []))}")
                for j, group in enumerate(section.get('groups', [])):
                    print(f"      Groupe {j+1}: {group.get('title', 'default')}")
                    print(f"        Champs: {len(group.get('fields', []))}")
        else:
            print("\n⚠️ Pas de 'config' dans metadata_json !")
            print(f"Keys disponibles: {list(metadata.keys()) if isinstance(metadata, dict) else 'None'}")

if __name__ == "__main__":
    asyncio.run(check_referentiel())
