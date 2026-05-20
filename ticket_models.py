from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = relationship("TicketComment", back_populates="ticket")

class TicketComment(Base):
    __tablename__ = "ticket_comments"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    author_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="comments")

class TicketAuditLog(Base):
    __tablename__ = "ticket_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    action = Column(String, nullable=False)
    actor = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)

MAX_TICKETS_PER_USER = 50
DEFAULT_TICKET_PRIORITY = "low"
SUPPORTED_STATUSES = ["open", "in_progress", "resolved", "closed"]
AUTO_CLOSE_DAYS = 30
ESCALATION_HOURS = 48

def get_status_description(status: str) -> str:
    descriptions = {
        "open": "Ticket is newly created and awaiting triage.",
        "in_progress": "An agent is currently working on the ticket.",
        "resolved": "The issue has been resolved but pending user confirmation.",
        "closed": "The ticket is finalized and closed."
    }
    return descriptions.get(status, "Unknown status.")
