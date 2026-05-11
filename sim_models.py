from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class SimCard(Base):
    __tablename__ = "sim_cards"

    id = Column(Integer, primary_key=True, index=True)
    iccid = Column(String, unique=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=True)
    
    subscriber = relationship("Subscriber")
