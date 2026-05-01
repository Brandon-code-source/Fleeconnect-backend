from pydantic import BaseModel
from typing import Optional


class ListingCreate(BaseModel):
    title: str
    make: str
    year: int
    mileage: Optional[int] = None
    price: float
    location: str
    phone: str
    images: list[str] = []
    user_id: int
    transmission: str | None = None
    engine_size: str | None = None
    fuel_type: str | None = None
    description: str | None = None


class ListingOut(BaseModel):
    id: int
    title: str
    make: str
    year: int
    mileage: Optional[int]
    price: float
    location: str
    phone: str
    images: list[str] = []
    status: str
    user_id: int | None = None
    transmission: str | None = None
    engine_size: str | None = None
    fuel_type: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    business_name: str

    email: str

    password: str

    phone: str

    location: str


class UserLogin(BaseModel):
    email: str

    password: str


class UserOut(BaseModel):
    id: int
    business_name: str
    email: str
    password: str
    phone: str | None = None
    location: str | None = None

    class Config:
        from_attributes = True
