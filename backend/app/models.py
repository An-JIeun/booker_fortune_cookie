from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class FortuneMessage(Base):
    __tablename__ = "fortune_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    new_year_message = Column(String, nullable=False)  # 설날 메시지
    book_recommendation = Column(String, nullable=False)  # 책 추천
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

