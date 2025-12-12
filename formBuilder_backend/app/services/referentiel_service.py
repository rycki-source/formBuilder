"""Service de gestion des référentiels de formulaires dynamiques"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.referentiel import Referentiel, ReferentielDonnees
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json

from app.schemas.referentiel import (
    ReferentielCreate,
    ReferentielUpdate,
)
from app.utils.excel_referentiel_parser import ExcelReferentielParser


class ReferentielService:
    """Service pour gérer les référentiels de formulaires dynamiques"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_referentiel(
        self,
        nom: str,
        source_type: str,
        metadata_json: Dict[str, Any],
        personne_import_id: int,
        config: Optional[Dict[str, Any]] = None,
        ref_id: Optional[str] = None,
        version: str = "1.0",
        is_template: bool = False,
        source_file: Optional[str] = None
    ) -> Referentiel:
        """Créer un référentiel"""
        # Fusionner config dans metadata_json si config est fourni
        if config:
            metadata_json = metadata_json or {}
            metadata_json['config'] = config
        
        try:
            new_ref = Referentiel(
                nom=nom,
                description=metadata_json.get('description'),
                version=version,
                source_type=source_type,
                metadata_json=metadata_json,
                personne_import_id=personne_import_id,
                valide=True,
            )
            self.db.add(new_ref)
            await self.db.commit()
            await self.db.refresh(new_ref)
            return new_ref
        except Exception as e:
            await self.db.rollback()
            print(f"❌ ERREUR CREATE REFERENTIEL: {e}")
            print(f"Type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def get_referentiel(self, referentiel_id: int, user_id: Optional[int] = None) -> Optional[Referentiel]:
        """Récupérer un référentiel"""
        query = select(Referentiel).where(Referentiel.id == referentiel_id)
        
        if user_id:
            query = query.where(
                or_(
                    Referentiel.personne_import_id == user_id,
                    Referentiel.is_template == True
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_referentiel_by_ref_id(self, ref_id: str) -> Optional[Referentiel]:
        """Récupérer un référentiel par ref_id"""
        result = await self.db.execute(
            select(Referentiel).where(Referentiel.ref_id == ref_id)
        )
        return result.scalar_one_or_none()

    async def list_referentiels(
        self,
        user_id: Optional[int] = None,
        is_template: Optional[bool] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Referentiel], int]:
        """Lister les référentiels avec filtres"""
        query = select(Referentiel)
        
        # Filtres
        conditions = []
        
        if user_id:
            conditions.append(
                or_(
                    Referentiel.personne_import_id == user_id,
                    Referentiel.is_template == True
                )
            )
        
        if is_template is not None:
            conditions.append(Referentiel.is_template == is_template)
        
        if is_active is not None:
            conditions.append(Referentiel.is_active == is_active)
        
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Referentiel.nom.ilike(search_pattern),
                    Referentiel.description.ilike(search_pattern)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Total
        count_query = select(Referentiel.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())
        
        # Pagination et tri
        query = query.order_by(Referentiel.date_import.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        referentiels = result.scalars().all()
        
        return list(referentiels), total

    async def update_referentiel(
        self,
        referentiel_id: int,
        user_id: int,
        **update_data
    ) -> Optional[Referentiel]:
        """Mettre à jour un référentiel"""
        referentiel = await self.get_referentiel(referentiel_id, user_id)
        
        if referentiel is None:
            return None
        
        # Vérifier les permissions (extraction de la valeur pour éviter Column comparison)
        if getattr(referentiel, 'personne_import_id', None) != user_id:
            return None
        
        # Mettre à jour les champs
        for key, value in update_data.items():
            if hasattr(referentiel, key) and value is not None:
                setattr(referentiel, key, value)
        
        if hasattr(referentiel, 'updated_at'):
            setattr(referentiel, 'updated_at', datetime.utcnow())
        
        await self.db.commit()
        await self.db.refresh(referentiel)
        
        return referentiel

    async def delete_referentiel(self, referentiel_id: int, user_id: int) -> bool:
        """Supprimer un référentiel"""
        referentiel = await self.get_referentiel(referentiel_id, user_id)
        
        if referentiel is None:
            return False
        
        # Vérifier les permissions (extraction de la valeur pour éviter Column comparison)
        if getattr(referentiel, 'personne_import_id', None) != user_id:
            return False
        
        await self.db.delete(referentiel)
        await self.db.commit()
        
        return True

    async def import_from_excel(
        self,
        file_path: str,
        user_id: int,
        save_as_template: bool = False,
        source_file_name: str | None = None
    ) -> Referentiel:
        """Importer un référentiel depuis un fichier Excel"""
        # Parser le fichier Excel
        referentiel_dict = ExcelReferentielParser.parse_excel_file(file_path)
        
        # Générer un nom unique si nécessaire
        nom_base = referentiel_dict["metadata"]["name"]
        nom = nom_base
        counter = 1
        
        # Vérifier si le nom existe déjà
        while True:
            existing = await self.db.execute(
                select(Referentiel).where(Referentiel.nom == nom)
            )
            if existing.scalar_one_or_none() is None:
                break
            nom = f"{nom_base} ({counter})"
            counter += 1
        
        # Créer le référentiel
        return await self.create_referentiel(
            nom=nom,
            source_type="excel",
            metadata_json=referentiel_dict["metadata"],
            personne_import_id=user_id,
            config=referentiel_dict["config"],
            ref_id=referentiel_dict["config"]["id"],
            version=referentiel_dict["version"],
            is_template=save_as_template,
            source_file=source_file_name
        )

    async def import_from_csv(
        self,
        file_path: str,
        user_id: int,
        save_as_template: bool = False,
        source_file_name: str | None = None
    ) -> Referentiel:
        """Importer un référentiel depuis un fichier CSV"""
        from app.utils.csv_referentiel_parser import CSVReferentielParser
        
        # Parser le fichier CSV
        referentiel_dict = CSVReferentielParser.parse_csv_file(file_path)
        
        # Générer un nom unique si nécessaire
        nom_base = referentiel_dict["config"]["name"]
        nom = nom_base
        counter = 1
        
        # Vérifier si le nom existe déjà
        while True:
            existing = await self.db.execute(
                select(Referentiel).where(Referentiel.nom == nom)
            )
            if existing.scalar_one_or_none() is None:
                break
            nom = f"{nom_base} ({counter})"
            counter += 1
        
        # Créer le référentiel
        return await self.create_referentiel(
            nom=nom,
            source_type="csv",
            metadata_json={
                "name": nom,
                "description": "Importé depuis CSV"
            },
            personne_import_id=user_id,
            config=referentiel_dict["config"],
            ref_id=referentiel_dict["config"]["id"],
            version=referentiel_dict["config"].get("version", "1.0.0"),
            is_template=save_as_template,
            source_file=source_file_name
        )

    async def import_from_json(
        self,
        json_content: str,
        user_id: int,
        source_file: Optional[str] = None,
        save_as_template: bool = False
    ) -> Referentiel:
        """Importer un référentiel depuis JSON"""
        referentiel_dict = json.loads(json_content)
        
        return await self.create_referentiel(
            nom=referentiel_dict["metadata"]["name"],
            source_type="json",
            metadata_json=referentiel_dict["metadata"],
            personne_import_id=user_id,
            config=referentiel_dict["config"],
            ref_id=referentiel_dict["config"]["id"],
            version=referentiel_dict.get("version", "1.0.0"),
            is_template=save_as_template
        )

    async def add_referentiel_data(
        self, referentiel_id: int, donnees: List[Dict[str, Any]]
    ):
        """Ajouter des données à un référentiel"""
        for item in donnees:
            ref_data = ReferentielDonnees(
                referentiel_id=referentiel_id, cle=item.get("cle"), valeur=item
            )
            self.db.add(ref_data)
        await self.db.commit()

    def convert_to_response(self, referentiel: Referentiel) -> Dict[str, Any]:
        """Convertir un référentiel en réponse API"""
        metadata_json = referentiel.metadata_json or {}
        config = metadata_json.get('config', {})
        
        # DEBUG: Afficher la structure
        print(f"\n🔍 convert_to_response pour référentiel ID {referentiel.id}")
        print(f"📦 metadata_json keys: {list(metadata_json.keys())}")
        print(f"⚙️  config keys: {list(config.keys()) if isinstance(config, dict) else 'NOT A DICT'}")
        if isinstance(config, dict) and 'sections' in config:
            print(f"📋 Nombre de sections dans config: {len(config['sections'])}")
            for i, section in enumerate(config.get('sections', [])):
                print(f"   Section {i}: {section.get('id')} - groups: {len(section.get('groups', []))}")
        else:
            print(f"⚠️  Pas de sections dans config !")
            print(f"⚠️  config = {config}")
        
        # S'assurer que config a au minimum la structure requise
        if not config or not isinstance(config, dict):
            config = {
                "id": "form",
                "version": "1.0.0",
                "name": referentiel.nom or "Formulaire",
                "sections": []
            }
        
        # Garantir que les champs obligatoires de FormConfig sont présents
        if "id" not in config:
            config["id"] = "form"
        if "version" not in config:
            config["version"] = "1.0.0"
        if "name" not in config:
            config["name"] = referentiel.nom or "Formulaire"
        if "sections" not in config:
            config["sections"] = []
        
        # Assurer que metadata a les champs requis
        metadata_response = {
            "name": referentiel.nom or "Formulaire",
            "description": referentiel.description or "",
            "author": metadata_json.get("author"),
            "tags": metadata_json.get("tags", [])
        }
        
        return {
            "id": referentiel.id,
            "ref_id": str(config.get('id', 'form')),
            "version": str(referentiel.version or "1.0"),
            "metadata": metadata_response,
            "config": config,
            "custom_validators": metadata_json.get('customValidators'),
            "custom_components": metadata_json.get('customComponents'),
            "source_type": str(referentiel.source_type),
            "source_file": metadata_json.get('source_file'),
            "is_active": True,
            "is_template": False,
            "valide": bool(referentiel.valide),
            "created_at": referentiel.date_import.isoformat() if referentiel.date_import is not None else datetime.utcnow().isoformat(),
            "updated_at": referentiel.date_import.isoformat() if referentiel.date_import is not None else datetime.utcnow().isoformat(),
            "personne_import_id": int(getattr(referentiel, 'personne_import_id', None) or 0)
        }
