from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# 데이터베이스 URL (SQLite 사용, Render에서는 PostgreSQL로 변경 가능)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fortune_cookie.db")

if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 2.0 스타일의 DeclarativeBase 사용 (Python 3.13 호환)
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

