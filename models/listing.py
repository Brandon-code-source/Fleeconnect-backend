from sqlalchemy import Column, Integer, String, Float
from database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    make = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    price = Column(Float)
    location = Column(String)
    phone = Column(String)
    images = Column(String)
    status = Column(String, default="active")
    user_id = Column(Integer, nullable=True)
    transmission = Column(String, nullable=True)
    engine_size = Column(String, nullable=True)
    fuel_type = Column(String, nullable=True)
    description = Column(String, nullable=True)
