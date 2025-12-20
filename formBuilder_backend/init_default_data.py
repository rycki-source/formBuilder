"""
Script pour initialiser les templates et données par défaut
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.template_service import TemplateService, seed_default_templates


async def init_default_data():
    """Initialiser les données par défaut"""
    async with AsyncSessionLocal() as db:
        print("🌱 Initialisation des templates par défaut...")
        
        # Seed les templates
        await seed_default_templates(db)
        
        # Créer des thèmes par défaut
        service = TemplateService(db)
        
        themes = [
            {
                "nom": "Moderne (Bleu)",
                "primary_color": "#3b82f6",
                "secondary_color": "#6366f1",
                "accent_color": "#8b5cf6",
                "background_color": "#ffffff",
                "text_color": "#1f2937"
            },
            {
                "nom": "Pro (Gris foncé)",
                "primary_color": "#1f2937",
                "secondary_color": "#374151",
                "accent_color": "#6b7280",
                "background_color": "#f9fafb",
                "text_color": "#111827"
            },
            {
                "nom": "Nature (Vert)",
                "primary_color": "#10b981",
                "secondary_color": "#059669",
                "accent_color": "#34d399",
                "background_color": "#ffffff",
                "text_color": "#064e3b"
            },
            {
                "nom": "Élégant (Violet)",
                "primary_color": "#8b5cf6",
                "secondary_color": "#7c3aed",
                "accent_color": "#a78bfa",
                "background_color": "#faf5ff",
                "text_color": "#4c1d95"
            }
        ]
        
        for theme_data in themes:
            try:
                await service.create_theme(**theme_data)
                print(f"✅ Thème créé: {theme_data['nom']}")
            except Exception as e:
                print(f"⚠️ Thème déjà existant: {theme_data['nom']}")
        
        print("\n✅ Initialisation terminée!")


if __name__ == "__main__":
    asyncio.run(init_default_data())
