from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.administrative_entity import AdministrativeEntity


class AdministrativeEntityDAO:
    
    def create_corporate_entity(self, db: Session, entity_data: dict) -> AdministrativeEntity:
        """
        Create a new administrative entity.
        """
        entity_dict = entity_data.model_dump()
        admin_entity = AdministrativeEntity(**entity_dict)
        db.add(admin_entity)
        db.commit()
        db.refresh(admin_entity)
        return admin_entity

    def get_all_corporate_entities(self, db: Session) -> List[AdministrativeEntity]:
        """
        Fetch all administrative entities.
        """
        entities = db.query(AdministrativeEntity).all()
        return [{"id": entity.id, "coorporate_name": entity.coorporate_name, "tax_id": entity.tax_id} for entity in entities]

    def get_corporate_entity_by_id(self, db: Session, entity_id: int) -> Optional[AdministrativeEntity]:
        """
        Fetch a administrative entity by its ID.
        """
        return db.query(AdministrativeEntity).filter(AdministrativeEntity.id == entity_id).first()
