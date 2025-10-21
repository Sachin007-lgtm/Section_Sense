"""
Contact Form Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ContactMessageCreate(BaseModel):
    """Schema for creating a contact message"""
    name: str = Field(..., min_length=2, max_length=200, description="Name of the person")
    email: EmailStr = Field(..., description="Email address")
    subject: Optional[str] = Field(None, max_length=300, description="Subject of the message")
    message: str = Field(..., min_length=10, description="Message content")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")


class ContactMessageResponse(BaseModel):
    """Schema for contact message response"""
    id: int
    name: str
    email: str
    subject: Optional[str]
    message: str
    phone: Optional[str]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContactMessageStatus(BaseModel):
    """Schema for updating message status"""
    is_read: bool
