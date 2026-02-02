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
    exclude_ids: str = Query(None, description="제외할 메시지 ID 목록 (쉼표로 구분)"),
    db: Session = Depends(get_db)
):
    """읽지 않은 랜덤 메시지 가져오기 (자신이 작성한 메시지 제외)"""
    # 제외할 메시지 ID 목록 파싱
    exclude_id_list = []
    if exclude_ids:
        try:
            exclude_id_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
        except ValueError:
            pass
    
    # 읽지 않은 메시지 중에서 자신이 작성한 메시지 제외
    query = db.query(FortuneMessage).filter(
        FortuneMessage.is_read == False
    )
    
    if exclude_id_list:
        query = query.filter(~FortuneMessage.id.in_(exclude_id_list))
    
    unread_messages = query.all()
    
    if not unread_messages:
        # 모든 메시지가 읽혔으면 전체에서 랜덤 선택 (자신이 작성한 메시지 제외)
        query = db.query(FortuneMessage)
        if exclude_id_list:
            query = query.filter(~FortuneMessage.id.in_(exclude_id_list))
        all_messages = query.all()
        
        if not all_messages:
            raise HTTPException(status_code=404, detail="메시지가 없습니다.")
        selected_message = random.choice(all_messages)
    else:
        selected_message = random.choice(unread_messages)
    
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

