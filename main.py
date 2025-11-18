import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Booking, ContactMessage

app = FastAPI(title="Kanojia Laundry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Kanojia Laundry backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Helper to convert ObjectId to str
class BookingOut(BaseModel):
    id: str
    name: str
    phone: str
    address: str
    service: str
    pickup_date: str | None = None
    notes: str | None = None


def serialize_booking(doc) -> BookingOut:
    return BookingOut(
        id=str(doc.get("_id")),
        name=doc.get("name", ""),
        phone=doc.get("phone", ""),
        address=doc.get("address", ""),
        service=doc.get("service", ""),
        pickup_date=(doc.get("pickup_date").isoformat() if doc.get("pickup_date") else None),
        notes=doc.get("notes")
    )


@app.post("/api/bookings", response_model=dict)
def create_booking(booking: Booking):
    try:
        inserted_id = create_document("booking", booking)
        return {"id": inserted_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bookings", response_model=List[BookingOut])
def list_bookings(limit: int = 50):
    try:
        docs = get_documents("booking", {}, limit)
        return [serialize_booking(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ContactOut(BaseModel):
    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    message: str


def serialize_contact(doc) -> ContactOut:
    return ContactOut(
        id=str(doc.get("_id")),
        name=doc.get("name", ""),
        email=doc.get("email"),
        phone=doc.get("phone"),
        message=doc.get("message", "")
    )


@app.post("/api/contacts", response_model=dict)
def create_contact(msg: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", msg)
        return {"id": inserted_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contacts", response_model=List[ContactOut])
def list_contacts(limit: int = 50):
    try:
        docs = get_documents("contactmessage", {}, limit)
        return [serialize_contact(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
