import time
import random
import uuid
import json
from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
import models
from logger_setup import logger, request_id_var
from pydantic import BaseModel
from typing import Optional

import sim_models
from sim_router import router as sim_api_router
import billing_models
from billing_router import router as billing_api_router

models.Base.metadata.create_all(bind=engine)
sim_models.Base.metadata.create_all(bind=engine)
billing_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(sim_api_router)
app.include_router(billing_api_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request_id_var.set(trace_id)
    
    logger.info(f"Incoming Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        if status_code == 422:
            logger.warning(f"Outgoing Response: {request.method} {request.url} | Status: {status_code} | Validation Error")
        elif status_code >= 500:
            logger.error(f"Outgoing Response: {request.method} {request.url} | Status: {status_code} | Internal Server Error")
        else:
            logger.info(f"Outgoing Response: {request.method} {request.url} | Status: {status_code}")
            
        return response
    except Exception as e:
        logger.error(f"Outgoing Response: {request.method} {request.url} | Status: 500 | Exception: {str(e)}", exc_info=True)
        raise

class SubscriberCreate(BaseModel):
    name: str
    phone_number: str
    plan_id: Optional[int] = None

class PlanUpdate(BaseModel):
    quota_gb: int

def call_vendor_provisioning_api():
    
    if random.choice([True, False, False]):
        logger.warning("Vendor API experiencing delays...")
        time.sleep(10)
    logger.info("Vendor API call completed.")

@app.post("/subscribers/")
def create_subscriber(sub: SubscriberCreate, db: Session = Depends(get_db)):
    db_sub = models.Subscriber(**sub.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    call_vendor_provisioning_api()
    return {"id": db_sub.id, "name": db_sub.name, "phone": db_sub.phone_number}

@app.get("/subscribers/{sub_id}")
def read_subscriber(sub_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == sub_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    
   
    plan_name = subscriber.plan.name
    
    return {
        "id": subscriber.id, 
        "name": subscriber.name, 
        "phone": subscriber.phone_number,
        "plan_name": plan_name
    }

@app.put("/subscribers/{sub_id}/plan")
def update_subscriber_plan(sub_id: int, plan: PlanUpdate, db: Session = Depends(get_db)):
    subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == sub_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    
    subscriber.plan_id = plan.quota_gb # simplistic update for testing validation error
    db.commit()
    logger.info(f"Updating plan quota to {plan.quota_gb}")
    return {"status": "Plan quota updated", "quota_gb": plan.quota_gb}

@app.delete("/subscribers/{sub_id}")
def deactivate_subscriber(sub_id: int):
    
    dangling_db = SessionLocal()
    subscriber = dangling_db.query(models.Subscriber).filter(models.Subscriber.id == sub_id).first()
    if subscriber:
        dangling_db.delete(subscriber)
        dangling_db.flush() # Locks the database
        logger.warning(f"Subscriber {sub_id} marked for deletion, transaction left open! (database is locked)")
    return {"status": "Deactivated"}
    
@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    if not db.query(models.DataPlan).first():
        p1 = models.DataPlan(name="Basic", price=10, quota_gb=5)
        p2 = models.DataPlan(name="Premium", price=20, quota_gb=50)
        db.add_all([p1, p2])
        db.commit()
    return {"status": "Seeded"}
