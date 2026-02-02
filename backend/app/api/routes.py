from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import FortuneMessage
from app.schemas import FortuneMessageCreate, FortuneMessageResponse
import random

router = APIRouter()

@router.post("/messages", response_model=FortuneMessageResponse)
def create_message(message: FortuneMessageCreate, db: Session = Depends(get_db)):
    """새로운 포춘 쿠키 메시지 생성"""
    db_message = FortuneMessage(
        new_year_message=message.new_year_message,
        book_recommendation=message.book_recommendation,
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    print(f"[DEBUG] 새 메시지 생성: id={db_message.id}, new_year_message={db_message.new_year_message[:50]}...")
    return db_message

@router.get("/messages/random", response_model=FortuneMessageResponse)
def get_random_message(
    db: Session = Depends(get_db),
    exclude_ids: str = Query(None, description="제외할 메시지 ID 목록 (쉼표로 구분)")
):
    """데이터베이스에서 읽지 않은 랜덤 메시지 가져오기 (자신이 작성한 메시지 제외)"""
    # 제외할 메시지 ID 목록 파싱
    exclude_id_list = []
    if exclude_ids:
        try:
            exclude_id_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
        except ValueError:
            pass
    
    print(f"[DEBUG] exclude_ids 파라미터: {exclude_ids}")
    print(f"[DEBUG] exclude_id_list: {exclude_id_list}")
    
    # 데이터베이스에서 전체 메시지 개수 확인
    total_count = db.query(FortuneMessage).count()
    print(f"[DEBUG] 데이터베이스 전체 메시지 개수: {total_count}")
    
    # 데이터베이스에서 모든 메시지 ID 확인
    all_message_ids = [msg.id for msg in db.query(FortuneMessage).all()]
    print(f"[DEBUG] 데이터베이스에 있는 모든 메시지 ID: {all_message_ids}")
    
    # 1단계: 데이터베이스에서 자신이 작성한 메시지를 제외한 전체 메시지 가져오기
    available_query = db.query(FortuneMessage)
    if exclude_id_list:
        available_query = available_query.filter(~FortuneMessage.id.in_(exclude_id_list))
    available_messages = available_query.all()  # 데이터베이스에서 직접 조회
    available_message_ids = [msg.id for msg in available_messages]
    print(f"[DEBUG] 데이터베이스에서 조회한 사용 가능한 메시지 개수 (자신이 작성한 메시지 제외): {len(available_messages)}")
    print(f"[DEBUG] 사용 가능한 메시지 ID: {available_message_ids}")
    
    if not available_messages:
        # 사용 가능한 메시지가 없으면 운영자의 기본 메시지 반환
        print("[DEBUG] ⚠️ 사용 가능한 메시지가 없어서 운영자 메시지 반환")
        print(f"[DEBUG] ⚠️ 전체 메시지: {total_count}개, 제외된 메시지: {len(exclude_id_list)}개")
        from datetime import datetime
        default_message = FortuneMessageResponse(
            id=0,
            new_year_message="올해도 꿈꾸시는 일 모두 이루시길 바랍니다! 2026년도 파이팅!!💪",
            book_recommendation="너의 유토피아(정보라) - 저주토끼로 유명한 정보라 작가의 SF 단편소설집입니다. SF 소설 좋아하신다면 읽어보시길 바라요!!",
            is_read=False,
            created_at=datetime.utcnow(),
            read_at=None
        )
        return default_message
    
    # 2단계: 데이터베이스에서 조회한 메시지 중에서 읽지 않은 메시지 우선 선택
    unread_available = [msg for msg in available_messages if not msg.is_read]
    print(f"[DEBUG] 읽지 않은 사용 가능한 메시지 개수: {len(unread_available)}")
    
    if unread_available:
        # 데이터베이스에서 조회한 메시지 중 랜덤 선택
        selected_message = random.choice(unread_available)
        print(f"[DEBUG] 데이터베이스에서 읽지 않은 메시지 선택: id={selected_message.id}")
    else:
        # 읽지 않은 메시지가 없으면 데이터베이스에서 조회한 전체 사용 가능한 메시지에서 선택
        selected_message = random.choice(available_messages)
        print(f"[DEBUG] 데이터베이스에서 전체 사용 가능한 메시지 선택: id={selected_message.id}")
    
    return selected_message

@router.patch("/messages/{message_id}/read", response_model=FortuneMessageResponse)
def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    """메시지를 읽음으로 표시"""
    message = db.query(FortuneMessage).filter(FortuneMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다.")
    
    message.is_read = True
    from datetime import datetime
    message.read_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    return message

@router.get("/messages/count")
def get_message_count(db: Session = Depends(get_db)):
    """전체 메시지 개수 조회 (데이터베이스에서 직접 카운트)"""
    # 데이터베이스에서 직접 전체 메시지 개수 조회
    count = db.query(FortuneMessage).count()
    print(f"[DEBUG] 데이터베이스에서 조회한 메시지 개수: {count}")
    
    # 실제 메시지 ID 목록도 확인 (디버깅용)
    all_ids = [msg.id for msg in db.query(FortuneMessage).all()]
    print(f"[DEBUG] 데이터베이스에 있는 메시지 ID 목록: {all_ids}")
    
    return {"count": count}

@router.get("/messages", response_model=list[FortuneMessageResponse])
def get_all_messages(db: Session = Depends(get_db)):
    """모든 메시지 조회 (FastAPI docs에서 확인 가능)"""
    # 데이터베이스에서 모든 메시지 조회
    messages = db.query(FortuneMessage).order_by(FortuneMessage.id.desc()).all()
    print(f"[DEBUG] 모든 메시지 조회: {len(messages)}개")
    return messages

@router.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """메시지 삭제 (FastAPI docs에서 테스트 가능)"""
    # 데이터베이스에서 메시지 조회
    message = db.query(FortuneMessage).filter(FortuneMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail=f"ID {message_id}인 메시지를 찾을 수 없습니다.")
    
    # 메시지 정보 저장 (삭제 전 로그용)
    deleted_message_info = {
        "id": message.id,
        "new_year_message": message.new_year_message[:50] + "..." if len(message.new_year_message) > 50 else message.new_year_message,
        "book_recommendation": message.book_recommendation[:50] + "..." if len(message.book_recommendation) > 50 else message.book_recommendation
    }
    
    # 메시지 삭제
    db.delete(message)
    db.commit()
    
    print(f"[DEBUG] 메시지 삭제 완료: id={message_id}")
    
    return {
        "message": "메시지가 성공적으로 삭제되었습니다.",
        "deleted_message": deleted_message_info
    }

