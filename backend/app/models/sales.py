from sqlalchemy import Column, Integer, String, Date, Float, Index
from ..db.base import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    product = Column(String(100), index=True)
    category = Column(String(50), index=True)
    amount = Column(Float)
    customer_age = Column(Integer)

    # Index composites pour les requêtes fréquentes
    __table_args__ = (
        Index('idx_date_category', 'date', 'category'),
        Index('idx_category_amount', 'category', 'amount'),
    ) 