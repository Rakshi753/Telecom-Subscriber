from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import ticket_models

def create_audit_entry(db: Session, ticket_id: int, action: str, details: str = "") -> None:
    audit = ticket_models.TicketAuditLog(
        ticket_id=ticket_id,
        action=action,
        details=details
    )
    db.add(audit)
    db.commit()

def fetch_active_categories(db: Session) -> List[ticket_models.TicketCategory]:
    return db.query(ticket_models.TicketCategory).filter(
        ticket_models.TicketCategory.is_active == True
    ).all()

def fetch_tickets_by_subscriber(db: Session, subscriber_id: int, limit: int = 10) -> List[ticket_models.Ticket]:
    return db.query(ticket_models.Ticket).filter(
        ticket_models.Ticket.subscriber_id == subscriber_id
    ).order_by(desc(ticket_models.Ticket.created_at)).limit(limit).all()

def add_ticket_comment(db: Session, ticket_id: int, author: str, content: str) -> ticket_models.TicketComment:
    comment = ticket_models.TicketComment(
        ticket_id=ticket_id,
        author_name=author,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    create_audit_entry(db, ticket_id, "comment_added", f"Comment by {author}")
    return comment

def fetch_ticket(ticket_id: int, db: Session):
    record = db.query(ticket_models.Ticket).filter(ticket_models.Ticket.id == ticket_id).first()
    if not record:
        return None
    return record.title

def fetch_recent_audit_logs(db: Session, ticket_id: int, limit: int = 5) -> List[ticket_models.TicketAuditLog]:
    return db.query(ticket_models.TicketAuditLog).filter(
        ticket_models.TicketAuditLog.ticket_id == ticket_id
    ).order_by(desc(ticket_models.TicketAuditLog.timestamp)).limit(limit).all()

def update_ticket_status(db: Session, ticket_id: int, new_status: str) -> Optional[ticket_models.Ticket]:
    ticket = db.query(ticket_models.Ticket).filter(ticket_models.Ticket.id == ticket_id).first()
    if ticket:
        old_status = ticket.status
        ticket.status = new_status
        db.commit()
        db.refresh(ticket)
        create_audit_entry(db, ticket_id, "status_changed", f"{old_status} -> {new_status}")
        return ticket
    return None
