from sqlalchemy.orm import Session
from app.dao.administrative_entity_dao import AdministrativeEntityDAO
from app.schemas.administrative_entity_schema import AdministrativeEntityResponse, AdministrativeEntityListResponse
from app.models.administrative_entity import AdministrativeEntity
from typing import List


class AdministrativeEntityService:
    def __init__(self, entity_dao: AdministrativeEntityDAO):
        self.entity_dao = entity_dao


    def create_administrative_entity(self, db: Session, entity_data: dict):
        corporate_entity = AdministrativeEntity(
            coorporate_name=entity_data['coorporate_name'],
            tax_id=entity_data['tax_id']
        )
        db.add(corporate_entity)
        db.commit()
        db.refresh(corporate_entity)
        return corporate_entity
    
    def get_all_administrative_entities(self, db: Session) -> List[AdministrativeEntityListResponse]:
        """
        Fetch all administrative entities.
        """
        entities = self.entity_dao.get_all_corporate_entities(db)
        return [AdministrativeEntityListResponse.model_validate(entity) for entity in entities]

    def get_administrative_entity_by_id(self, db: Session, entity_id: int) -> AdministrativeEntityResponse:
        """
        Fetch a administrative entity by its ID.
        """
        entity = self.entity_dao.get_corporate_entity_by_id(db, entity_id)
        if not entity:
            raise ValueError("administrative entity not found")
        return AdministrativeEntityResponse.model_validate(entity)
