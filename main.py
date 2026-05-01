from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.user import User
from models.lead import Lead
from database import engine, SessionLocal, Base
from models.listing import Listing
from schemas import ListingCreate, ListingOut, UserCreate, UserLogin, UserOut
import json
import random
import string

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "FleetConnect backend running 🚗"}


@app.post("/listings", response_model=ListingOut)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    data = listing.model_dump()

    data["images"] = json.dumps(data.get("images", []))

    new_listing = Listing(**data)
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    # convert string back to list before returning
    new_listing.images = json.loads(new_listing.images or "[]")

    return new_listing


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        business_name=user.business_name,
        email=user.email,
        password=user.password,
        phone=user.phone,
        location=user.location,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Account created successfully",
        "user_id": new_user.id,
        "business_name": new_user.business_name,
        "email": new_user.email,
        "phone": new_user.phone,
        "location": new_user.location,
    }


@app.get("/listings")
def get_listings(db: Session = Depends(get_db)):
    listings = db.query(Listing).all()

    results = []

    for listing in listings:
        owner = db.query(User).filter(User.id == listing.user_id).first()

        results.append(
            {
                "id": listing.id,
                "title": listing.title,
                "make": listing.make,
                "year": listing.year,
                "mileage": listing.mileage,
                "price": listing.price,
                "location": listing.location,
                "phone": listing.phone,
                "status": listing.status,
                "user_id": listing.user_id,
                "owner_name": owner.business_name if owner else None,
                "owner_email": owner.email if owner else None,
                "images": json.loads(listing.images or "[]"),
                "transmission": listing.transmission,
                "engine_size": listing.engine_size,
                "fuel_type": listing.fuel_type,
                "description": listing.description,
            }
        )

    return results


@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    db.delete(listing)
    db.commit()

    return {"message": "Listing deleted"}


@app.put("/listings/{listing_id}")
def update_listing(listing_id: int, data: ListingCreate, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.title = data.title
    listing.make = data.make
    listing.year = data.year
    listing.mileage = data.mileage
    listing.price = data.price
    listing.location = data.location
    listing.phone = data.phone
    listing.images = json.dumps(data.images)

    db.commit()
    db.refresh(listing)

    return listing


@app.put("/listings/{listing_id}/sold")
def mark_sold(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.status == "sold":
        listing.status = "available"
    else:
        listing.status = "sold"

    db.commit()
    db.refresh(listing)

    return listing


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    found_user = db.query(User).filter(User.email.ilike(user.email.strip())).first()

    if not found_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not found_user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")

    if found_user.password != user.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {
        "message": "Login successful",
        "user_id": found_user.id,
        "business_name": found_user.business_name,
        "email": found_user.email,
        "phone": found_user.phone,
        "location": found_user.location,
    }


@app.post("/lead/{listing_id}")
def create_lead(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    new_lead = Lead(listing_id=listing.id, user_id=listing.user_id)

    db.add(new_lead)
    db.commit()

    return {"message": "Lead tracked"}


@app.get("/leads/{user_id}")
def get_leads(user_id: int, db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.user_id == user_id).all()

    return {"total_leads": len(leads)}


@app.put("/dealers/{user_id}")
def update_dealer(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.phone = data.get("phone", user.phone)
    user.location = data.get("location", user.location)

    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "business_name": user.business_name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location,
    }


@app.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


@app.put("/users/{user_id}/suspend")
def suspend_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User suspended"}


@app.post("/reset-password")
def reset_password(email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email.ilike(email.strip())).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # generate temporary password

    temp_password = "".join(random.choices(string.ascii_letters + string.digits, k=8))

    user.password = temp_password

    db.commit()

    return {
        "message": "Password reset",
        "temp_password": temp_password,  # ⚠️ for now (dev only)
    }


@app.put("/change-password/{user_id}")
def change_password(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = data.get("password")
    db.commit()

    return {"message": "Password updated"}
