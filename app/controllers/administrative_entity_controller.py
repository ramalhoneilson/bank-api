from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.administrative_entity_service import AdministrativeEntityService
from app.dao.administrative_entity_dao import AdministrativeEntityDAO
from app.schemas.administrative_entity_schema import AdministrativeEntityCreate, AdministrativeEntityResponse, AdministrativeEntityListResponse

router = APIRouter()


@router.post("/administrative_entity", response_model=AdministrativeEntityResponse)
def create_corporate_entity(entity_data: AdministrativeEntityCreate, db: Session = Depends(get_db)):
    try:
        entity_dao = AdministrativeEntityDAO()
        entity_service = AdministrativeEntityService(entity_dao)
        # TODO: check why we need to pass the entire Pydantic model, not just model_dump()
        new_entity = entity_service.create_administrative_entity(db, entity_data.model_dump())
        return new_entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/administrative-entities", response_model=List[AdministrativeEntityListResponse])
def list_all_administrative_entities(db: Session = Depends(get_db)):
    """
    List all administrative entities.
    """
    try:
        entity_dao = AdministrativeEntityDAO()
        entity_service = AdministrativeEntityService(entity_dao)

        entities = entity_service.get_all_administrative_entities(db)
        return entities

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/administrative_entity/{entity_id}", response_model=AdministrativeEntityResponse)
def get_corporate_entity_details(entity_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific administrative entity by its ID.
    """
    try:
        entity_dao = AdministrativeEntityDAO()
        entity_service = AdministrativeEntityService(entity_dao)

        entity = entity_service.get_administrative_entity_by_id(db, entity_id)
        return entity

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
