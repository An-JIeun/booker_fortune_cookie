from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.routes import router

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fortune Cookie API", version="1.0.0")

# CORS 설정 (Vue 앱과 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["fortune"])

@app.get("/")
def root():
    return {"message": "Fortune Cookie API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

