from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, field_serializer


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class AccessTokenSchema(BaseModel):
    id: int
    type: str
    token_details: Dict[str, Any]
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()
