from pydantic import BaseModel


class AdministrativeEntityBase(BaseModel):
    tax_id: str


class AdministrativeEntityCreate(AdministrativeEntityBase):
    coorporate_name: str


class AdministrativeEntityResponse(AdministrativeEntityBase):
    tax_id: str

    class Config:
        from_attributes = True


class AdministrativeEntityListResponse(BaseModel):
    id: int
    coorporate_name: str
    tax_id: str

    class Config:
        from_attributes = True
