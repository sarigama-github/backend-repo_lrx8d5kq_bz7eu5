"""
Database Schemas for Kanojia Laundry

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name. Example: Booking -> "booking"
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class Booking(BaseModel):
    """
    Customer pickup booking requests
    Collection: booking
    """
    name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="WhatsApp/Phone number")
    address: str = Field(..., description="Pickup address")
    service: Literal['Washing', 'Ironing', 'Washing + Ironing', 'Pickup & Delivery'] = Field(
        'Washing + Ironing', description="Selected service"
    )
    pickup_date: Optional[date] = Field(None, description="Preferred pickup date")
    notes: Optional[str] = Field(None, description="Additional notes")

class ContactMessage(BaseModel):
    """
    General inquiries from contact form
    Collection: contactmessage
    """
    name: str = Field(..., description="Sender name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone/WhatsApp number")
    message: str = Field(..., description="Message body")
