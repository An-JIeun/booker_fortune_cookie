from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.routes import router
import os

# 데이터베이스 테이블 생성
# 기본값을 production으로 해서, ENVIRONMENT 미설정 시에도 테이블을 절대 삭제하지 않음
# (Render 등에서 ENVIRONMENT를 안 넣으면 기존엔 development로 동작해 매 재시작마다 drop_all 되었음)
environment = os.getenv("ENVIRONMENT", "production")
if environment == "development":
    Base.metadata.drop_all(bind=engine)
    print("[DEBUG] 개발 환경: 기존 테이블 삭제 후 재생성")
else:
    print("[DEBUG] 프로덕션 환경: 기존 테이블 유지, 없으면 생성")
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

