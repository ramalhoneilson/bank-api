from pydantic import BaseModel
from pydantic.dataclasses import ConfigDict


class AdministrativeEntityCreate(BaseModel):
    tax_id: str
    coorporate_name: str


class AdministrativeEntityResponse(BaseModel):
    id: int
    tax_id: str
    coorporate_name: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )


class AdministrativeEntityListResponse(BaseModel):
    id: int
    coorporate_name: str
    tax_id: str

