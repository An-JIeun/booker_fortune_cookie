from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# 데이터베이스 URL (SQLite 사용, Render에서는 PostgreSQL 사용)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fortune_cookie.db")

# Render는 postgres:// 를 주는데, SQLAlchemy는 postgresql:// 만 인식함
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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

