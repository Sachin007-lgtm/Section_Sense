from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import os
from groq import Groq
import logging
import json
import asyncio
from datetime import datetime

from app.database import get_db
from app.models.chat_models import ChatConversation, ChatMessage
from app.schemas import (
    ChatMessageSchema, SaveConversationRequest, 
    ConversationResponse, ConversationDetailResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Groq client
groq_client = None
try:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        groq_client = Groq(api_key=api_key)
        logger.info("Groq client initialized for chatbot")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.8


@router.post("/chatbot/stream")
async def chatbot_stream(request: ChatRequest):
    """
    Streaming chatbot endpoint - sends response word by word like ChatGPT
    
    This provides a better user experience with real-time streaming responses
    """
    if not groq_client:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is currently unavailable."
        )

    async def generate():
        try:
            # Build conversation history
            messages = [
                {
                    "role": "system",
                    "content": """You are Kamado, a friendly and knowledgeable AI assistant specializing in Indian Criminal Law. You chat naturally like ChatGPT - conversational, clear, and helpful.

Your expertise covers:
- Bharatiya Nyaya Sanhita (BNS) - the new criminal code
- Bharatiya Nagarik Suraksha Sanhita (BNSS) - new criminal procedure code
- Bharatiya Sakshya Adhiniyam (BSA) - new evidence law
- And their old equivalents: IPC, CrPC, and Indian Evidence Act

How you respond:
- Chat naturally and conversationally, like talking to a friend
- Keep answers concise and to the point - avoid long formal explanations unless specifically asked
- Use simple, plain language that anyone can understand
- DO NOT use any markdown formatting like asterisks (**), bold, italic, or special symbols
- Write in plain text only - no special formatting at all
- Only give detailed breakdowns if the user asks for more details
- When answering "why" questions, directly address what they're actually asking about
- Skip the formal legal disclaimers unless it's a serious legal advice request

For example:
❌ DON'T: Use markdown like "**BNS applies**" or formatting symbols
❌ DON'T: Give formal structured responses with "1. What the section covers, 2. Key provisions..."
✅ DO: Answer directly in plain text like "BNS applies to all of India because it's the main criminal law code that replaced the old IPC. When someone commits a crime anywhere in India, BNS sections are what determine if it's illegal and what the punishment is."

Stay helpful, brief, conversational, and use ONLY plain text with no special formatting.
"""
                }
            ]
            
            # Add conversation history (last 10 messages)
            for msg in request.history[-10:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # Stream response from Groq
            stream = groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.1-8b-instant",
                temperature=0.7,  # Slightly higher for more natural conversation
                max_tokens=1024,  # Shorter responses, more concise
                top_p=0.9,
                stream=True  # Enable streaming
            )
            
            # Send chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # Send as JSON with data: prefix for SSE format
                    yield f"data: {json.dumps({'content': content})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for smooth streaming
            
            # Send end signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chatbot", response_model=ChatResponse)
async def chatbot_interaction(request: ChatRequest):
    """
    Chatbot endpoint for legal assistance using Groq AI
    
    NOTE: This chatbot uses Groq's LLM (llama-3.1-8b-instant) trained knowledge 
    about Indian criminal law. It does NOT query the local database.
    
    The AI provides general legal information based on:
    - Its training on Indian legal texts (BNS, BNSS, BSA)
    - General knowledge of criminal law principles
    - Conversation context from chat history
    
    This approach allows for:
    ✓ Natural language understanding
    ✓ Contextual responses
    ✓ Explanations beyond database content
    ✓ Comparison with old laws (IPC/CrPC)
    """
    try:
        if not groq_client:
            raise HTTPException(
                status_code=503,
                detail="Chatbot service is currently unavailable. Please check API configuration."
            )
        
        # Build conversation history for context
        messages = [
            {
                "role": "system",
                "content": """You are Kamado, a friendly and knowledgeable AI assistant specializing in Indian Criminal Law. You chat naturally like ChatGPT - conversational, clear, and helpful.

Your expertise covers:
- Bharatiya Nyaya Sanhita (BNS) - the new criminal code
- Bharatiya Nagarik Suraksha Sanhita (BNSS) - new criminal procedure code
- Bharatiya Sakshya Adhiniyam (BSA) - new evidence law
- And their old equivalents: IPC, CrPC, and Indian Evidence Act

How you respond:
- Chat naturally and conversationally, like talking to a friend
- Keep answers concise and to the point - avoid long formal explanations unless specifically asked
- Use simple, plain language that anyone can understand
- DO NOT use any markdown formatting like asterisks (**), bold, italic, or special symbols
- Write in plain text only - no special formatting at all
- Only give detailed breakdowns if the user asks for more details
- When answering "why" questions, directly address what they're actually asking about
- Skip the formal legal disclaimers unless it's a serious legal advice request

For example:
❌ DON'T: Use markdown like "**BNS applies**" or formatting symbols
❌ DON'T: Give formal structured responses with "1. What the section covers, 2. Key provisions..."
✅ DO: Answer directly in plain text like "BNS applies to all of India because it's the main criminal law code that replaced the old IPC. When someone commits a crime anywhere in India, BNS sections are what determine if it's illegal and what the punishment is."

Stay helpful, brief, conversational, and use ONLY plain text with no special formatting.
"""
            }
        ]
        
        # Add conversation history (last 10 messages for context)
        for msg in request.history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Get response from Groq
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,  # Higher for more natural conversation
            max_tokens=1024,  # Shorter, more concise responses
            top_p=0.9,
            stream=False
        )
        
        response_text = chat_completion.choices[0].message.content
        
        return ChatResponse(
            response=response_text,
            confidence=0.85
        )
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.get("/chatbot/health")
async def chatbot_health():
    """Check chatbot service health"""
    return {
        "status": "healthy" if groq_client else "unavailable",
        "service": "Kamado Legal Chatbot",
        "model": "llama-3.1-8b-instant",
        "provider": "Groq"
    }


# =============================================================================
# Chat Storage Endpoints
# =============================================================================

@router.post("/chatbot/conversations/save")
async def save_conversation(
    request: SaveConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Save or update a chatbot conversation in the database
    
    This allows conversations to persist across devices and browser sessions
    """
    try:
        # Check if conversation already exists
        existing = db.query(ChatConversation).filter(
            ChatConversation.conversation_id == request.conversation_id
        ).first()
        
        if existing:
            # Update existing conversation
            existing.title = request.title or existing.title
            existing.updated_at = datetime.utcnow()
            
            # Delete old messages and add new ones
            db.query(ChatMessage).filter(
                ChatMessage.conversation_id == request.conversation_id
            ).delete()
            
            conversation = existing
        else:
            # Create new conversation
            conversation = ChatConversation(
                conversation_id=request.conversation_id,
                title=request.title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(conversation)
        
        # Add messages
        for msg in request.messages:
            message = ChatMessage(
                conversation_id=request.conversation_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp or datetime.utcnow(),
                message_metadata=msg.metadata
            )
            db.add(message)
        
        db.commit()
        
        return {
            "success": True,
            "conversation_id": request.conversation_id,
            "message": "Conversation saved successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save conversation: {str(e)}"
        )


@router.get("/chatbot/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get list of all conversations
    
    Returns a summary of conversations with metadata
    """
    try:
        conversations = db.query(ChatConversation)\
            .filter(ChatConversation.is_active == True)\
            .order_by(ChatConversation.updated_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        result = []
        for conv in conversations:
            result.append(ConversationResponse(
                conversation_id=conv.conversation_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=len(conv.messages)
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversations: {str(e)}"
        )


@router.get("/chatbot/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with all its messages
    """
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        messages = []
        for msg in conversation.messages:
            messages.append(ChatMessageSchema(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.message_metadata
            ))
        
        return ConversationDetailResponse(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            messages=messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation: {str(e)}"
        )


@router.delete("/chatbot/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation (soft delete by setting is_active=False)
    """
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        conversation.is_active = False
        db.commit()
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )
