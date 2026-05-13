from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import sim_models
import models
from logger_setup import logger
from pydantic import BaseModel
import sys

router = APIRouter(prefix="/sim", tags=["SIM Cards"])

class SimCreate(BaseModel):
    iccid: str
    subscriber_id: int

@router.post("/")
def create_sim(sim: SimCreate, db: Session = Depends(get_db)):

    if len(sim.iccid) == 10:
        logger.error(f"Failed to create SIM: ICCID {sim.iccid} length is 10. Activation system rejected it.")
        raise HTTPException(status_code=400, detail="Invalid ICCID length rejected by network.")
        
    db_sim = sim_models.SimCard(iccid=sim.iccid, subscriber_id=sim.subscriber_id)
    db.add(db_sim)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create SIM. ICCID might already exist or subscriber missing.")
        
    db.refresh(db_sim)
    return {"id": db_sim.id, "iccid": db_sim.iccid, "subscriber_id": db_sim.subscriber_id}

@router.post("/{sim_id}/provision")
def provision_sim(sim_id: int, db: Session = Depends(get_db)):
    sim = db.query(sim_models.SimCard).filter(sim_models.SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="SIM not found")
        
    
    if sim.iccid == "0000000000000000000":
        logger.fatal("CRITICAL SYSTEM FAILURE: HLR Provisioning Gateway unreachable. Data corruption imminent.")
        raise HTTPException(status_code=500, detail="Critical System Failure")
        
    return {"status": "Provisioned", "iccid": sim.iccid}

@router.get("/{sim_id}")
def get_sim(sim_id: int, db: Session = Depends(get_db)):
    sim = db.query(sim_models.SimCard).filter(sim_models.SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="SIM not found")
    return {"id": sim.id, "iccid": sim.iccid, "subscriber_id": sim.subscriber_id}
