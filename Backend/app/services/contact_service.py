"""
Contact Form Service
"""
from sqlalchemy.orm import Session
from app.models.contact_models import ContactMessage
from app.schemas.contact_schemas import ContactMessageCreate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ContactService:
    """Service for handling contact form submissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(self, message_data: ContactMessageCreate) -> ContactMessage:
        """
        Create a new contact message
        
        Args:
            message_data: Contact message data
            
        Returns:
            ContactMessage: Created message
        """
        try:
            db_message = ContactMessage(
                name=message_data.name,
                email=message_data.email,
                subject=message_data.subject,
                message=message_data.message,
                phone=message_data.phone
            )
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            logger.info(f"Contact message created from {message_data.email}")
            return db_message
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating contact message: {str(e)}")
            raise
    
    def get_all_messages(self, skip: int = 0, limit: int = 100) -> List[ContactMessage]:
        """
        Get all contact messages
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[ContactMessage]: List of messages
        """
        return self.db.query(ContactMessage)\
            .order_by(ContactMessage.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_message_by_id(self, message_id: int) -> Optional[ContactMessage]:
        """
        Get a specific contact message by ID
        
        Args:
            message_id: Message ID
            
        Returns:
            Optional[ContactMessage]: Message if found
        """
        return self.db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    
    def mark_as_read(self, message_id: int) -> Optional[ContactMessage]:
        """
        Mark a message as read
        
        Args:
            message_id: Message ID
            
        Returns:
            Optional[ContactMessage]: Updated message if found
        """
        message = self.get_message_by_id(message_id)
        if message:
            message.is_read = True
            self.db.commit()
            self.db.refresh(message)
            logger.info(f"Message {message_id} marked as read")
        return message
    
    def delete_message(self, message_id: int) -> bool:
        """
        Delete a contact message
        
        Args:
            message_id: Message ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        message = self.get_message_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            logger.info(f"Message {message_id} deleted")
            return True
        return False
    
    def get_unread_count(self) -> int:
        """
        Get count of unread messages
        
        Returns:
            int: Number of unread messages
        """
        return self.db.query(ContactMessage).filter(ContactMessage.is_read == False).count()
