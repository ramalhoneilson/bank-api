from sqlalchemy.orm import Session
from app.dao.administrative_entity_dao import AdministrativeEntityDAO
from app.schemas.administrative_entity_schema import AdministrativeEntityResponse, AdministrativeEntityListResponse
from app.models.administrative_entity import AdministrativeEntity
from typing import List


class AdministrativeEntityService:
    def __init__(self, entity_dao: AdministrativeEntityDAO):
        self.entity_dao = entity_dao


    def create_administrative_entity(self, db: Session, entity_data: dict):
        if not entity_data.coorporate_name:
            raise ValueError("Company name cannot be empty")
        if not entity_data.tax_id:
            raise ValueError("Tax Id cannot be empty")

        created_entity = self.entity_dao.create_corporate_entity(db, entity_data)

        entity_dict = {
            "id": created_entity.id,
            "coorporate_name": created_entity.coorporate_name,
            "tax_id": created_entity.tax_id
        }
        return AdministrativeEntityResponse.model_validate(entity_dict)
    
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
