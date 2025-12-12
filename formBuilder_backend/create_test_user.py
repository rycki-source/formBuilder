"""Créer l'utilisateur test"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        # Vérifier si l'utilisateur existe
        result = await db.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ User exists: {user.email} (role: {user.role})")
        else:
            print("❌ User NOT FOUND - Creating...")
            user = User(
                email="test@example.com",
                nom="Test",
                prenom="User",
                mot_de_passe=hash_password("testpassword123"),
                role="admin",
                statut="actif"
            )
            db.add(user)
            await db.commit()
            print("✅ User created successfully")

if __name__ == "__main__":
    asyncio.run(main())
