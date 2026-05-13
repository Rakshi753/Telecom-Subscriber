from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    amount = Column(Float)
    status = Column(String, default="unpaid")
