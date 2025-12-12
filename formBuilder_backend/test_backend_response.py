"""Test pour vérifier la réponse du backend après import Excel"""
import asyncio
import sys
import json
from app.db.session import AsyncSessionLocal
from app.services.referentiel_service import ReferentielService
from sqlalchemy import select
from app.models.referentiel import Referentiel

async def test_backend_response():
    """Tester la conversion d'un référentiel en réponse"""
    async with AsyncSessionLocal() as db:
        service = ReferentielService(db)
        
        # Récupérer le dernier référentiel créé
        result = await db.execute(
            select(Referentiel).order_by(Referentiel.id.desc()).limit(1)
        )
        referentiel = result.scalar_one_or_none()
        
        if not referentiel:
            print("❌ Aucun référentiel trouvé dans la base")
            return
        
        print(f"✅ Référentiel trouvé: ID={referentiel.id}, nom={referentiel.nom}")
        print(f"📦 metadata_json: {json.dumps(referentiel.metadata_json, indent=2, ensure_ascii=False)}")
        
        # Convertir en réponse
        print("\n" + "="*80)
        print("🔄 Conversion en réponse API...")
        print("="*80)
        
        response = service.convert_to_response(referentiel)
        
        print("\n📤 RÉPONSE API:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Vérifier les sections
        print("\n" + "="*80)
        print("✅ VÉRIFICATION:")
        sections = response.get("config", {}).get("sections", [])
        print(f"Nombre de sections: {len(sections)}")
        
        for i, section in enumerate(sections, 1):
            print(f"\n📌 Section {i}:")
            print(f"   ID: {section.get('id')}")
            print(f"   Title: {section.get('title')}")
            print(f"   Groups: {len(section.get('groups', []))}")
            
            for j, group in enumerate(section.get('groups', []), 1):
                print(f"   └─ Groupe {j}: {group.get('id')}")
                print(f"      Fields: {len(group.get('fields', []))}")
                for field in group.get('fields', []):
                    print(f"      └─ {field.get('id')}: {field.get('label')}")

if __name__ == "__main__":
    asyncio.run(test_backend_response())
