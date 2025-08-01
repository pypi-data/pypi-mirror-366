from pydantic import BaseModel, Field


class SpecimenModel(BaseModel):
    institution: str | None
    collection: str | None
    barcode: str
    pid: str = Field(alias='specimen_pid')
    preparation_types: list[str]
    asset_preparation_type: str
