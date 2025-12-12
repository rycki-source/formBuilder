"""
Script de test pour vérifier que les nouveaux types de champs fonctionnent
"""
import sys
sys.path.insert(0, '.')

from app.services.validation_service import ValidationService
import json


def test_geolocation_validation():
    """Tester la validation de géolocalisation"""
    print("\n🧪 Test Géolocalisation")
    print("=" * 50)
    
    # Structure avec champ géolocalisation
    structure = {
        "champs": [
            {
                "id": "position",
                "label": "Position",
                "type_champ": "geolocation",
                "obligatoire": True
            }
        ]
    }
    
    # Test 1: Données valides
    donnees_valides = {
        "position": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "accuracy": 10
        }
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_valides, structure)
    print(f"✅ Données valides: {valide} (erreurs: {erreurs})")
    assert valide, "Les données valides doivent passer"
    
    # Test 2: Latitude invalide
    donnees_invalides = {
        "position": {
            "latitude": 100,  # > 90
            "longitude": 2.3522
        }
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_invalides, structure)
    print(f"❌ Latitude invalide: {valide} (erreurs: {erreurs})")
    assert not valide, "Les coordonnées invalides doivent échouer"
    
    # Test 3: Structure invalide
    donnees_invalides = {
        "position": "string invalide"
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_invalides, structure)
    print(f"❌ Structure invalide: {valide} (erreurs: {erreurs})")
    assert not valide, "Le format invalide doit échouer"
    
    # Test 4: Champ manquant (obligatoire)
    donnees_vides = {}
    valide, erreurs = ValidationService.validate_soumission(donnees_vides, structure)
    print(f"❌ Champ obligatoire manquant: {valide} (erreurs: {erreurs})")
    assert not valide, "Le champ obligatoire manquant doit échouer"


def test_signature_validation():
    """Tester la validation de signature"""
    print("\n🧪 Test Signature")
    print("=" * 50)
    
    structure = {
        "champs": [
            {
                "id": "signature_client",
                "label": "Signature",
                "type_champ": "signature",
                "obligatoire": True
            }
        ]
    }
    
    # Test 1: Signature valide (base64)
    donnees_valides = {
        "signature_client": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_valides, structure)
    print(f"✅ Signature valide: {valide} (erreurs: {erreurs})")
    assert valide, "La signature valide doit passer"
    
    # Test 2: Format invalide
    donnees_invalides = {
        "signature_client": "texte invalide"
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_invalides, structure)
    print(f"❌ Format invalide: {valide} (erreurs: {erreurs})")
    assert not valide, "Le format invalide doit échouer"
    
    # Test 3: Type invalide
    donnees_invalides = {
        "signature_client": {"invalid": "object"}
    }
    valide, erreurs = ValidationService.validate_soumission(donnees_invalides, structure)
    print(f"❌ Type invalide: {valide} (erreurs: {erreurs})")
    assert not valide, "Le type invalide doit échouer"


def test_csv_parser():
    """Tester le parser CSV avec les nouveaux types"""
    print("\n🧪 Test Parser CSV")
    print("=" * 50)
    
    from app.utils.csv_referentiel_parser import CSVReferentielParser
    
    # Parser le template
    result = CSVReferentielParser.parse_csv_file("template_referentiel.csv")
    
    sections = result['config']['sections']
    print(f"✅ Sections trouvées: {len(sections)}")
    
    # Chercher les nouveaux types de champs
    all_fields = []
    for section in sections:
        for group in section.get('groups', []):
            all_fields.extend(group.get('fields', []))
    
    geolocation_fields = [f for f in all_fields if f.get('type') == 'geolocation']
    signature_fields = [f for f in all_fields if f.get('type') == 'signature']
    
    print(f"✅ Champs géolocalisation: {len(geolocation_fields)}")
    print(f"✅ Champs signature: {len(signature_fields)}")
    
    assert len(geolocation_fields) > 0, "Au moins un champ géolocalisation doit exister"
    assert len(signature_fields) > 0, "Au moins un champ signature doit exister"
    
    # Afficher les détails
    for field in geolocation_fields:
        print(f"  - {field.get('label')} (ID: {field.get('id')})")
    
    for field in signature_fields:
        print(f"  - {field.get('label')} (ID: {field.get('id')})")


if __name__ == "__main__":
    print("\n🚀 TESTS DES NOUVEAUX TYPES DE CHAMPS")
    print("=" * 50)
    
    try:
        test_geolocation_validation()
        test_signature_validation()
        test_csv_parser()
        
        print("\n" + "=" * 50)
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
