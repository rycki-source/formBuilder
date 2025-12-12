"""Endpoints pour les référentiels"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional
import tempfile
import os

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.referentiel_service import ReferentielService
from app.schemas.referentiel import (
    ReferentielCreate,
    ReferentielUpdate,
    ReferentielResponse,
    ReferentielList,
    ReferentielImportRequest,
    ReferentielImportResponse
)

router = APIRouter(prefix="/referentiels", tags=["referentiels"])


@router.post("/", response_model=ReferentielResponse, status_code=status.HTTP_201_CREATED)
async def create_referentiel(
    referentiel: ReferentielCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Créer un nouveau référentiel manuellement.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "UTILISATEUR_NON_AUTHENTIFIE",
                "message": "Impossible d'identifier l'utilisateur",
                "action": "Reconnectez-vous à l'application"
            }
        )
    
    try:
        new_ref = await service.create_referentiel(
            version=referentiel.version,
            metadata=referentiel.metadata,
            config=referentiel.config,
            source_type=referentiel.source_type or "manual",
            custom_validators=referentiel.custom_validators,
            custom_components=referentiel.custom_components,
            tags=referentiel.tags,
            is_template=referentiel.is_template or False,
            is_active=referentiel.is_active if referentiel.is_active is not None else True,
            user_id=user_id
        )
        return service.convert_to_response(new_ref)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ECHOUEE",
                "message": f"Erreur de validation: {str(e)}",
                "action": "Vérifiez les données du référentiel et corrigez les erreurs"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ERREUR_CREATION_REFERENTIEL",
                "message": f"Erreur lors de la création: {str(e)}",
                "action": "Réessayez ou contactez l'administrateur"
            }
        )


@router.get("/", response_model=ReferentielList)
async def list_referentiels(
    is_template: Optional[bool] = Query(None, description="Filtrer par template"),
    is_active: Optional[bool] = Query(None, description="Filtrer par actif"),
    search: Optional[str] = Query(None, description="Recherche texte"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lister tous les référentiels accessibles par l'utilisateur.
    Inclut les référentiels de l'utilisateur + les templates publics.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    skip = (page - 1) * page_size
    referentiels, total = await service.list_referentiels(
        user_id=user_id,
        is_template=is_template,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=page_size
    )
    
    items = [service.convert_to_response(ref) for ref in referentiels]
    
    return ReferentielList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/templates", response_model=ReferentielList)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lister uniquement les templates publics.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    skip = (page - 1) * page_size
    referentiels, total = await service.list_referentiels(
        user_id=user_id,
        is_template=True,
        is_active=True,
        search=search,
        skip=skip,
        limit=page_size
    )
    
    items = [service.convert_to_response(ref) for ref in referentiels]
    
    return ReferentielList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{referentiel_id}", response_model=ReferentielResponse)
async def get_referentiel(
    referentiel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer un référentiel par son ID.
    """
    service = ReferentielService(db)
    referentiel = await service.get_referentiel(referentiel_id, current_user.id)
    
    if not referentiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Référentiel non trouvé"
        )
    
    return service.convert_to_response(referentiel)


@router.get("/by-ref-id/{ref_id}", response_model=ReferentielResponse)
async def get_referentiel_by_ref_id(
    ref_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer un référentiel par son ref_id unique.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    referentiel = await service.get_referentiel_by_ref_id(ref_id, user_id)
    
    if not referentiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Référentiel avec ref_id '{ref_id}' non trouvé"
        )
    
    return service.convert_to_response(referentiel)


@router.put("/{referentiel_id}", response_model=ReferentielResponse)
async def update_referentiel(
    referentiel_id: int,
    update_data: ReferentielUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mettre à jour un référentiel existant.
    Seul le propriétaire peut modifier.
    """
    service = ReferentielService(db)
    
    # Vérifier que l'utilisateur est propriétaire
    user_id = getattr(current_user, 'id', None)
    existing = await service.get_referentiel(referentiel_id, user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Référentiel non trouvé"
        )
    
    if getattr(existing, 'personne_import_id', None) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de modifier ce référentiel"
        )
    
    try:
        updated = await service.update_referentiel(referentiel_id, update_data)
        return service.convert_to_response(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{referentiel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referentiel(
    referentiel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprimer un référentiel.
    Seul le propriétaire peut supprimer.
    """
    service = ReferentielService(db)
    
    # Vérifier que l'utilisateur est propriétaire
    user_id = getattr(current_user, 'id', None)
    existing = await service.get_referentiel(referentiel_id, user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Référentiel non trouvé"
        )
    
    if getattr(existing, 'personne_import_id', None) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de supprimer ce référentiel"
        )
    
    success = await service.delete_referentiel(referentiel_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )


@router.post("/import/excel", response_model=ReferentielImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_excel(
    file: UploadFile = File(...),
    save_as_template: bool = Query(False, description="Sauvegarder comme template public"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Importer un référentiel depuis un fichier Excel.
    
    Le fichier doit contenir les feuilles suivantes :
    - Metadata : Configuration globale
    - Sections : Définition des sections
    - Fields : Définition des champs
    - Options : Options pour select/radio/checkbox
    - Validation : Règles de validation
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format Excel (.xlsx ou .xls)"
        )
    
    # Sauvegarder temporairement le fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        service = ReferentielService(db)
        user_id = getattr(current_user, 'id', None)
        referentiel = await service.import_from_excel(
            file_path=tmp_path,
            user_id=user_id,
            save_as_template=save_as_template,
            source_file_name=file.filename
        )
        
        response_data = service.convert_to_response(referentiel)
        print(f"🔍 Response data: {response_data}")
        print(f"🔍 Version: {response_data.get('version')} (type: {type(response_data.get('version'))})")
        print(f"🔍 Metadata: {response_data.get('metadata')} (type: {type(response_data.get('metadata'))})")
        print(f"🔍 Config: {response_data.get('config')} (type: {type(response_data.get('config'))})")
        
        return ReferentielImportResponse(
            success=True,
            message="Référentiel importé avec succès depuis Excel",
            referentiel=response_data,
            warnings=[]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de parsing Excel : {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import : {str(e)}"
        )
    finally:
        # Supprimer le fichier temporaire
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                # Sur Windows, le fichier peut être verrouillé temporairement
                # On réessaie après un court délai
                import time
                time.sleep(0.1)
                try:
                    os.remove(tmp_path)
                except:
                    # Si ça échoue encore, on log mais on ne bloque pas
                    import logging
                    logging.warning(f"Impossible de supprimer le fichier temporaire: {tmp_path}")


@router.post("/import/csv", response_model=ReferentielImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_csv(
    file: UploadFile = File(...),
    save_as_template: bool = Query(False, description="Sauvegarder comme template public"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Importer un référentiel depuis un fichier CSV.
    
    Le CSV doit contenir les colonnes suivantes :
    - Section : Nom de la section
    - Field ID : Identifiant unique du champ
    - Field Label : Libellé du champ
    - Field Type : Type (text, email, number, select, etc.)
    - Required : true/false
    - Options : Options séparées par ";" pour select/radio
    - Validation Rules : Règles format "key:value" séparées par ";"
    - Conditions : Conditions format "field:operator:value" séparées par ";"
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format CSV (.csv)"
        )
    
    # Sauvegarder temporairement le fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8') as tmp_file:
        content = await file.read()
        tmp_file.write(content.decode('utf-8'))
        tmp_path = tmp_file.name
    
    try:
        service = ReferentielService(db)
        user_id = getattr(current_user, 'id', None)
        referentiel = await service.import_from_csv(
            file_path=tmp_path,
            user_id=user_id,
            save_as_template=save_as_template,
            source_file_name=file.filename
        )
        
        response_data = service.convert_to_response(referentiel)
        
        return ReferentielImportResponse(
            success=True,
            message="Référentiel importé avec succès depuis CSV",
            referentiel=response_data,
            warnings=[]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de parsing CSV : {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import : {str(e)}"
        )
    finally:
        # Supprimer le fichier temporaire
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                import time
                time.sleep(0.1)
                try:
                    os.remove(tmp_path)
                except:
                    import logging
                    logging.warning(f"Impossible de supprimer le fichier temporaire: {tmp_path}")


@router.post("/import/json", response_model=ReferentielImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_json_file(
    file: UploadFile = File(...),
    save_as_template: bool = Query(False, description="Sauvegarder comme template public"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Importer un référentiel depuis un fichier JSON.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être au format JSON (.json)"
        )
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        service = ReferentielService(db)
        user_id = getattr(current_user, 'id', None)
        referentiel = await service.import_from_json(
            json_content=content_str,
            user_id=user_id,
            save_as_template=save_as_template,
            source_file_name=file.filename
        )
        
        return ReferentielImportResponse(
            success=True,
            message="Référentiel importé avec succès depuis JSON",
            referentiel=service.convert_to_response(referentiel),
            warnings=[]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de parsing JSON : {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import : {str(e)}"
        )


@router.post("/import/text", response_model=ReferentielImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_text(
    import_request: ReferentielImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Importer un référentiel depuis du texte JSON/YAML collé.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    
    try:
        referentiel = await service.import_from_json(
            json_content=import_request.content,
            user_id=user_id,
            save_as_template=import_request.save_as_template,
            source_file_name=None
        )
        
        return ReferentielImportResponse(
            success=True,
            message=f"Référentiel importé avec succès depuis {import_request.source_type}",
            referentiel=service.convert_to_response(referentiel),
            warnings=[]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de parsing : {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import : {str(e)}"
        )


@router.post("/{referentiel_id}/export", response_model=Dict)
async def export_referentiel(
    referentiel_id: int,
    format: str = Query("json", regex="^(json|yaml)$", description="Format d'export"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exporter un référentiel au format JSON ou YAML.
    """
    service = ReferentielService(db)
    user_id = getattr(current_user, 'id', None)
    referentiel = await service.get_referentiel(referentiel_id, user_id)
    
    if not referentiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Référentiel non trouvé"
        )
    
    response_data = service.convert_to_response(referentiel)
    
    if format == "yaml":
        # TODO: Implémenter l'export YAML
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Export YAML non encore implémenté"
        )
    
    return response_data.model_dump()
