from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.administrative_entity import AdministrativeEntity


class AdministrativeEntityDAO:
    
    def create_corporate_entity(self, db: Session, entity_data: dict) -> AdministrativeEntity:
        """
        Create a new administrative entity.
        """
        entity = AdministrativeEntity(**entity_data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get_all_corporate_entities(self, db: Session) -> List[AdministrativeEntity]:
        """
        Fetch all administrative entities.
        """
        return db.query(AdministrativeEntity).all()

    def get_corporate_entity_by_id(self, db: Session, entity_id: int) -> Optional[AdministrativeEntity]:
        """
        Fetch a administrative entity by its ID.
        """
        return db.query(AdministrativeEntity).filter(AdministrativeEntity.id == entity_id).first()
