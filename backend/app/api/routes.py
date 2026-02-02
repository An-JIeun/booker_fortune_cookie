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
    return db_message

@router.get("/messages/random", response_model=FortuneMessageResponse)
def get_random_message(
    db: Session = Depends(get_db),
    exclude_ids: str = Query(None, description="제외할 메시지 ID 목록 (쉼표로 구분)")
):
    """읽지 않은 랜덤 메시지 가져오기 (자신이 작성한 메시지 제외)"""
    # 제외할 메시지 ID 목록 파싱
    exclude_id_list = []
    if exclude_ids:
        try:
            exclude_id_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
        except ValueError:
            pass
    
    print(f"[DEBUG] exclude_ids 파라미터: {exclude_ids}")
    print(f"[DEBUG] exclude_id_list: {exclude_id_list}")
    
    # 전체 메시지 개수 확인
    total_count = db.query(FortuneMessage).count()
    print(f"[DEBUG] 전체 메시지 개수: {total_count}")
    
    # 1단계: 자신이 작성한 메시지를 제외한 전체 메시지 가져오기
    available_query = db.query(FortuneMessage)
    if exclude_id_list:
        available_query = available_query.filter(~FortuneMessage.id.in_(exclude_id_list))
    available_messages = available_query.all()
    print(f"[DEBUG] 사용 가능한 메시지 개수 (자신이 작성한 메시지 제외): {len(available_messages)}")
    
    if not available_messages:
        # 사용 가능한 메시지가 없으면 운영자의 기본 메시지 반환
        print("[DEBUG] 사용 가능한 메시지가 없어서 운영자 메시지 반환")
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
    
    # 2단계: 사용 가능한 메시지 중에서 읽지 않은 메시지 우선 선택
    unread_available = [msg for msg in available_messages if not msg.is_read]
    print(f"[DEBUG] 읽지 않은 사용 가능한 메시지 개수: {len(unread_available)}")
    
    if unread_available:
        selected_message = random.choice(unread_available)
        print(f"[DEBUG] 읽지 않은 메시지에서 선택: id={selected_message.id}")
    else:
        # 읽지 않은 메시지가 없으면 전체 사용 가능한 메시지에서 선택
        selected_message = random.choice(available_messages)
        print(f"[DEBUG] 전체 사용 가능한 메시지에서 선택: id={selected_message.id}")
    
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
    """전체 메시지 개수 조회"""
    count = db.query(FortuneMessage).count()
    return {"count": count}

