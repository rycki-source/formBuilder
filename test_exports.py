"""
Script de test pour les exports HTML et PDF
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_html_export(formulaire_id: int, token: str):
    """Tester l'export HTML"""
    print(f"\n🔍 Test export HTML pour formulaire {formulaire_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/formulaires/{formulaire_id}/html", headers=headers)
    
    if response.status_code == 200:
        print("✅ Export HTML réussi")
        print(f"   Taille: {len(response.text)} caractères")
        
        # Sauvegarder le fichier
        with open(f"formulaire_{formulaire_id}.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"   Fichier sauvegardé: formulaire_{formulaire_id}.html")
        return True
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        return False


def test_pdf_export(formulaire_id: int, token: str):
    """Tester l'export PDF"""
    print(f"\n🔍 Test export PDF pour formulaire {formulaire_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/formulaires/{formulaire_id}/pdf", headers=headers)
    
    if response.status_code == 200:
        print("✅ Export PDF réussi")
        print(f"   Taille: {len(response.content)} octets")
        
        # Sauvegarder le fichier
        filename = f"formulaire_{formulaire_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"   Fichier sauvegardé: {filename}")
        return True
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        return False


def login(email: str, password: str):
    """Se connecter et obtenir le token"""
    print(f"\n🔐 Connexion avec {email}...")
    
    # FastAPI OAuth2 utilise form-data pour le login
    data = {
        "username": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Connexion réussie")
        return token
    else:
        print(f"❌ Erreur de connexion: {response.status_code}")
        print(response.text)
        return None


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Test des exports HTML et PDF")
    print("=" * 60)
    
    # Configuration
    EMAIL = "admin@test.com"
    PASSWORD = "Admin123!"
    FORMULAIRE_ID = 1
    
    # Permettre de passer les arguments en ligne de commande
    if len(sys.argv) > 1:
        FORMULAIRE_ID = int(sys.argv[1])
    if len(sys.argv) > 2:
        EMAIL = sys.argv[2]
    if len(sys.argv) > 3:
        PASSWORD = sys.argv[3]
    
    # Connexion
    token = login(EMAIL, PASSWORD)
    if not token:
        print("\n❌ Impossible de se connecter. Arrêt du test.")
        return
    
    # Tests
    html_ok = test_html_export(FORMULAIRE_ID, token)
    pdf_ok = test_pdf_export(FORMULAIRE_ID, token)
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Export HTML: {'✅ OK' if html_ok else '❌ ÉCHEC'}")
    print(f"Export PDF:  {'✅ OK' if pdf_ok else '❌ ÉCHEC'}")
    print("=" * 60)
    
    if html_ok and pdf_ok:
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("\nVous pouvez maintenant:")
        print(f"  - Ouvrir formulaire_{FORMULAIRE_ID}.html dans un navigateur")
        print(f"  - Ouvrir formulaire_{FORMULAIRE_ID}.pdf avec un lecteur PDF")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    main()
