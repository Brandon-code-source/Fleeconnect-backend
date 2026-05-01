from sqlalchemy import Column, Integer, String, Float
from database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    make = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    images = Column(String, nullable=True)
    status = Column(String, default="active")
    
