from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
import ticket_models
from pydantic import BaseModel
from typing import List, Optional
import ticket_controller

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketCreate(BaseModel):
    title: str
    description: str
    subscriber_id: int

class TicketStatusUpdate(BaseModel):
    status: str

@router.post("/")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    payload = ticket.dict()
    orchestration_result = ticket_controller.orchestrate_ticket_creation(payload, db)
    
    if not orchestration_result["success"]:
        raise HTTPException(status_code=400, detail=orchestration_result.get("error"))
        
    db_ticket = ticket_models.Ticket(
        title=ticket.title,
        description=ticket.description,
        subscriber_id=ticket.subscriber_id,
        status="open",
        priority=orchestration_result["assigned_priority"]
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/{ticket_id}")
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(ticket_models.Ticket).filter(ticket_models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}/status")
def update_status(ticket_id: int, update_data: TicketStatusUpdate, db: Session = Depends(get_db)):
    result = ticket_controller.handle_status_change(ticket_id, update_data.status, db)
    if "Failed" in result["message"]:
        raise HTTPException(status_code=400, detail="Invalid status or ticket not found")
    return result

@router.get("/{ticket_id}/formatted_title")
def read_formatted_title(ticket_id: int, db: Session = Depends(get_db)):
    formatted_title = ticket_controller.format_ticket_title(ticket_id, db)
    return {"formatted_title": formatted_title}

@router.get("/subscriber/{subscriber_id}/dashboard")
def get_dashboard(subscriber_id: int, db: Session = Depends(get_db)):
    return ticket_controller.build_subscriber_dashboard(subscriber_id, db)
