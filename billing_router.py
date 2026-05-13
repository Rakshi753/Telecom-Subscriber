import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
import billing_models
from logger_setup import logger
from pydantic import BaseModel

router = APIRouter(prefix="/billing", tags=["Billing"])

class InvoiceCreate(BaseModel):
    subscriber_id: int
    amount: float

@router.post("/invoices/")
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = billing_models.Invoice(subscriber_id=invoice.subscriber_id, amount=invoice.amount)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return {"id": db_invoice.id, "amount": db_invoice.amount, "status": db_invoice.status}

@router.post("/invoices/{invoice_id}/refund")
def refund_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(billing_models.Invoice).filter(billing_models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    
    gateway_url = os.getenv("PAYMENT_GATEWAY_URL")
    if not gateway_url:
        logger.error("Failed to process refund: PAYMENT_GATEWAY_URL is not configured.")
        raise HTTPException(status_code=500, detail="Payment Gateway Configuration Missing")
        
    invoice.status = "refunded"
    db.commit()
    return {"status": "Refunded", "invoice_id": invoice.id}

@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    
    if authorization != "Bearer ADMIN_TOKEN":
        logger.warning(f"Unauthorized deletion attempt for invoice {invoice_id}")
        
    
    invoice = db.query(billing_models.Invoice).filter(billing_models.Invoice.id == invoice_id).first()
    if invoice:
        db.delete(invoice)
        db.commit()
    return {"status": "Deleted"}
