"""Script pour debugger l'import Excel et vérifier la structure du référentiel"""
import sys
import json
from app.utils.excel_referentiel_parser import ExcelReferentielParser

if __name__ == "__main__":
    file_path = "test_formulaire.xlsx"
    
    print(f"🔍 Parse du fichier: {file_path}")
    print("=" * 80)
    
    try:
        referentiel = ExcelReferentielParser.parse_excel_file(file_path)
        
        print("\n📋 STRUCTURE DU RÉFÉRENTIEL:")
        print(json.dumps(referentiel, indent=2, ensure_ascii=False))
        
        print("\n\n✅ VÉRIFICATION DES SECTIONS:")
        sections = referentiel.get("config", {}).get("sections", [])
        print(f"Nombre de sections: {len(sections)}")
        
        for i, section in enumerate(sections, 1):
            print(f"\n📌 Section {i}: {section.get('title', 'Sans titre')}")
            print(f"   ID: {section.get('id')}")
            print(f"   Groupes: {len(section.get('groups', []))}")
            
            for j, group in enumerate(section.get("groups", []), 1):
                print(f"   └─ Groupe {j}: {group.get('title', 'default')}")
                print(f"      Champs: {len(group.get('fields', []))}")
                
                for field in group.get("fields", []):
                    print(f"      └─ {field.get('id')}: {field.get('label')} ({field.get('type')})")
        
        if not sections:
            print("⚠️  AUCUNE SECTION TROUVÉE !")
            print("Le formulaire ne sera pas affiché dans le frontend.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
