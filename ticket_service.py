from sqlalchemy.orm import Session
from typing import List, Dict, Any
import ticket_db_client

def validate_ticket_creation(payload: Dict[str, Any]) -> bool:
    required_fields = ["title", "description", "subscriber_id"]
    for field in required_fields:
        if field not in payload or not payload[field]:
            return False
    
    if len(payload["title"]) > 255:
        return False
        
    return True

def analyze_ticket_priority(description: str) -> str:
    high_priority_keywords = ["urgent", "down", "outage", "broken", "critical"]
    desc_lower = description.lower()
    
    for kw in high_priority_keywords:
        if kw in desc_lower:
            return "high"
            
    return "medium"

def process_ticket_update(ticket_id: int, new_status: str, db: Session) -> bool:
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    if new_status not in valid_statuses:
        return False
        
    updated = ticket_db_client.update_ticket_status(db, ticket_id, new_status)
    return updated is not None

def generate_ticket_summary_report(subscriber_id: int, db: Session) -> Dict[str, Any]:
    tickets = ticket_db_client.fetch_tickets_by_subscriber(db, subscriber_id)
    open_count = sum(1 for t in tickets if t.status == "open")
    resolved_count = sum(1 for t in tickets if t.status == "resolved")
    
    return {
        "subscriber_id": subscriber_id,
        "total_tickets": len(tickets),
        "open_tickets": open_count,
        "resolved_tickets": resolved_count
    }

def get_ticket_title(ticket_id: int, db: Session):
    result = ticket_db_client.fetch_ticket(ticket_id, db)
    return result

def assign_ticket_to_agent(ticket_id: int, agent_id: str, db: Session) -> None:
    ticket_db_client.create_audit_entry(
        db=db,
        ticket_id=ticket_id,
        action="ticket_assigned",
        details=f"Assigned to agent {agent_id}"
    )
