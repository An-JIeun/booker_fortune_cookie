from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FortuneMessageCreate(BaseModel):
    new_year_message: str
    book_recommendation: str

class FortuneMessageResponse(BaseModel):
    id: int
    new_year_message: str
    book_recommendation: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

