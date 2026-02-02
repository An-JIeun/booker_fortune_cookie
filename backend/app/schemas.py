from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FortuneMessageCreate(BaseModel):
    message: str

class FortuneMessageResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

