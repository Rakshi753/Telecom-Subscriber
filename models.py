from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DataPlan(Base):
    __tablename__ = "data_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    quota_gb = Column(Integer)

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    plan_id = Column(Integer, ForeignKey("data_plans.id"), nullable=True)

    plan = relationship("DataPlan")
