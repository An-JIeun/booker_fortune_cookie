# 🍪 포춘 쿠키 웹 서비스

FastAPI 백엔드와 Vue 프론트엔드를 사용한 포춘 쿠키 웹 서비스입니다.

## 기능

1. 사용자가 메시지를 입력하고 서버에 저장
2. 다른 사용자가 작성한 메시지를 랜덤으로 받아서 포춘 쿠키 형태로 표시
3. 클릭/터치 시 포춘 쿠키가 열리는 애니메이션 효과
4. 모바일 환경 친화적인 반응형 디자인

## 프로젝트 구조

```
booker_fortune_cookie/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py      # FastAPI 앱 진입점
│   │   ├── database.py  # 데이터베이스 설정
│   │   ├── models.py    # SQLAlchemy 모델
│   │   ├── schemas.py   # Pydantic 스키마
│   │   └── api/
│   │       └── routes.py # API 라우트
│   └── requirements.txt
├── frontend/            # Vue 프론트엔드
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── views/
│   │       └── Home.vue
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── render.yaml          # Render 배포 설정
```

## 로컬 개발 환경 설정

### 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

백엔드는 `http://localhost:8000`에서 실행됩니다.

### 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

## Render 배포

1. Render 대시보드에서 새 Web Service 생성
2. GitHub 저장소 연결
3. `render.yaml` 파일의 설정 사용
4. 환경 변수 설정:
   - `DATABASE_URL`: PostgreSQL 데이터베이스 URL (Render에서 자동 생성 가능)

## API 엔드포인트

- `POST /api/messages`: 새 메시지 생성
- `GET /api/messages/random`: 랜덤 메시지 가져오기
- `PATCH /api/messages/{id}/read`: 메시지를 읽음으로 표시

## 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **프론트엔드**: Vue 3, Vue Router, Axios, Vite
- **배포**: Render

