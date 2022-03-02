from fastapi.encoders import jsonable_encoder
from .objectid import PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime


class Asset(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    companyName: str
    type: str
    friendlyName: str
    companyId: PydanticObjectId = Field(None, alias="companyId")
    slug: str
    date_added: Optional[datetime]
    date_updated: Optional[datetime]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data
