from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    product = Column(String(100))
    category = Column(String(50))
    amount = Column(Float)
    customer_age = Column(Integer) 