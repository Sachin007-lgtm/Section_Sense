from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import get_db, engine
from app.models.law_models import Base
from app.models.contact_models import ContactMessage
from app.schemas import (
    SearchRequest, SearchResult, CaseUploadRequest, QARequest, QAResponse,
    SearchType, UserType, SystemHealth, SearchAnalytics, ExplanationRequest, ExplanationResponse
)
from app.schemas.contact_schemas import ContactMessageCreate, ContactMessageResponse, ContactMessageStatus
from app.services.universal_search_service import UniversalSearchService
from app.services.explanation_service import LegalExplanationService
from app.services.contact_service import ContactService
from app.services import chatbot_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Criminal Law Knowledge Base",
    description="A comprehensive legal search and recommendation system for criminal law",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)
# Ensure contact_messages table is created
ContactMessage.metadata.create_all(bind=engine)

# Include routers
app.include_router(chatbot_service.router, tags=["Chatbot"])

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Criminal Law Knowledge Base API")
    logger.info("Database tables created/verified")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Criminal Law Knowledge Base API")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Criminal Law Knowledge Base API",
        "version": "1.0.0",
        "description": "A comprehensive legal search and recommendation system",
        "endpoints": {
            "search": "/api/v1/search",
            "explain": "/api/v1/explain",
            "qa": "/api/v1/qa",
            "cases": "/api/v1/cases",
            "sections": "/api/v1/sections",
            "analytics": "/api/v1/analytics",
            "health": "/api/v1/health",
            "contact": "/api/v1/contact"
        }
    }

@app.get("/health", tags=["System"])
async def uptime_health_check():
    """Lightweight health check endpoint for uptime monitoring services"""
    logger.info("🩺 Health check ping received from UptimeRobot")
    return {"status": "ok"}

@app.get("/api/v1/health", response_model=SystemHealth, tags=["System"])
async def health_check():
    """Check system health and status"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    return SystemHealth(
        status="healthy" if db_connected else "unhealthy",
        database_connected=db_connected,
        search_index_healthy=True,  # Placeholder
        total_sections=0,  # Will be implemented
        total_cases=0,     # Will be implemented
        last_data_update=None,
        system_uptime="0 days, 0 hours"
    )


@app.get("/api/v1/database/info", tags=["System"])
async def database_info():
    """Get database information - shows if using PostgreSQL (Supabase) or SQLite"""
    from app.database import DATABASE_URL
    
    try:
        db = next(get_db())
        
        # Determine database type
        is_postgres = DATABASE_URL.startswith("postgresql")
        db_type = "PostgreSQL (Supabase)" if is_postgres else "SQLite (Local)"
        
        # Get database version
        if is_postgres:
            result = db.execute("SELECT version()").fetchone()
            db_version = result[0] if result else "Unknown"
            
            # Get table count
            table_result = db.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """).fetchone()
            table_count = table_result[0] if table_result else 0
            
            # Get law sections count
            sections_result = db.execute("SELECT COUNT(*) FROM law_sections").fetchone()
            sections_count = sections_result[0] if sections_result else 0
            
            # Get chat conversations count
            try:
                chats_result = db.execute("SELECT COUNT(*) FROM chat_conversations").fetchone()
                chats_count = chats_result[0] if chats_result else 0
            except:
                chats_count = 0
            
            return {
                "database_type": db_type,
                "database_version": db_version,
                "connection_url": DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else "N/A",
                "is_cloud_database": True,
                "total_tables": table_count,
                "law_sections_count": sections_count,
                "chat_conversations_count": chats_count,
                "status": "Connected ✅"
            }
        else:
            # SQLite
            result = db.execute("SELECT sqlite_version()").fetchone()
            db_version = f"SQLite {result[0]}" if result else "Unknown"
            
            sections_result = db.execute("SELECT COUNT(*) FROM law_sections").fetchone()
            sections_count = sections_result[0] if sections_result else 0
            
            return {
                "database_type": db_type,
                "database_version": db_version,
                "connection_url": "Local File",
                "is_cloud_database": False,
                "law_sections_count": sections_count,
                "status": "Connected ✅"
            }
            
    except Exception as e:
        logger.error(f"Database info error: {e}")
        return {
            "database_type": "Unknown",
            "status": f"Error: {str(e)}",
            "is_cloud_database": False
        }

@app.post("/api/v1/search", response_model=SearchResult, tags=["Search"])
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Perform legal search based on query and type"""
    try:
        start_time = time.time()
        
        # Initialize search service
        search_service = UniversalSearchService()
        
        # Perform search
        if request.search_type == SearchType.SECTION_SEARCH:
            sections = search_service.search_sections(
                query=request.query,
                filters=request.filters,
                max_results=request.max_results
            )
            result = SearchResult(
                query=request.query,
                search_type=request.search_type,
                total_results=len(sections),
                execution_time=0.0,  # Will be updated below
                results=sections,
                suggestions=search_service.get_suggestions(request.query),
                filters_applied=request.filters
            )
        else:
            # For other search types, return empty results for now
            result = SearchResult(
                query=request.query,
                search_type=request.search_type,
                total_results=0,
                execution_time=0.0,
                results=[],
                suggestions=[],
                filters_applied=request.filters
            )
        
        # Update execution time
        result.execution_time = time.time() - start_time
        
        return result
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/v1/search/sections", tags=["Search"])
async def search_sections(
    query: str = Query(..., min_length=3, description="Search query for law sections"),
    category: Optional[str] = Query(None, description="Filter by category"),
    bailable: Optional[str] = Query(None, description="Filter by bailable status"),
    cognizable: Optional[str] = Query(None, description="Filter by cognizable status"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    user_type: Optional[UserType] = Query(None, description="Type of user making the search"),
    db: Session = Depends(get_db)
):
    """Search for law sections with filters"""
    try:
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if bailable:
            filters['bailable'] = bailable
        if cognizable:
            filters['cognizable'] = cognizable
        
        # Create search request
        search_request = SearchRequest(
            query=query,
            search_type=SearchType.SECTION_SEARCH,
            user_type=user_type,
            filters=filters,
            max_results=max_results
        )
        
        # Perform search using Universal Search Service
        search_service = UniversalSearchService()
        sections = search_service.search_sections(
            query=query,
            filters=filters,
            max_results=max_results
        )
        
        result = SearchResult(
            query=query,
            search_type=SearchType.SECTION_SEARCH,
            total_results=len(sections),
            execution_time=0.0,
            results=sections,
            suggestions=[],
            filters_applied=filters
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Section search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Section search failed: {str(e)}")

@app.get("/api/v1/search/cases", tags=["Search"])
async def search_cases(
    query: str = Query(..., min_length=3, description="Search query for legal cases"),
    court: Optional[str] = Query(None, description="Filter by court"),
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    verdict: Optional[str] = Query(None, description="Filter by verdict"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    user_type: Optional[UserType] = Query(None, description="Type of user making the search"),
    db: Session = Depends(get_db)
):
    """Search for legal cases with filters"""
    try:
        # Build filters
        filters = {}
        if court:
            filters['court'] = court
        if case_type:
            filters['case_type'] = case_type
        if verdict:
            filters['verdict'] = verdict
        
        # Create search request
        search_request = SearchRequest(
            query=query,
            search_type=SearchType.CASE_SEARCH,
            user_type=user_type,
            filters=filters,
            max_results=max_results
        )
        
        # Perform search using Universal Search Service
        # Note: Case search not fully implemented yet
        result = SearchResult(
            query=query,
            search_type=SearchType.CASE_SEARCH,
            total_results=0,
            execution_time=0.0,
            results=[],
            suggestions=[],
            filters_applied=filters
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Case search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Case search failed: {str(e)}")

@app.post("/api/v1/explain", response_model=ExplanationResponse, tags=["Explanation"])
async def explain_section(
    request: ExplanationRequest,
    db: Session = Depends(get_db)
):
    """Generate plain-language explanation of a legal section"""
    try:
        # Initialize explanation service
        explanation_service = LegalExplanationService()
        
        # Generate explanation
        explanation = explanation_service.generate_explanation(request)
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")

@app.post("/api/v1/qa", response_model=QAResponse, tags=["Q&A"])
async def legal_qa(
    request: QARequest,
    db: Session = Depends(get_db)
):
    """Get legal Q&A response"""
    try:
        # For now, return a basic response
        # In production, this would integrate with an LLM or legal expert system
        
        answer = f"Based on your question about '{request.question}', here are the relevant legal considerations..."
        
        return QAResponse(
            question=request.question,
            answer=answer,
            confidence_score=0.8,
            relevant_sections=[],
            relevant_cases=[],
            sources=["Legal Database", "Case Law"],
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@app.post("/api/v1/cases/upload", tags=["Cases"])
async def upload_case(
    request: CaseUploadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload a new legal case"""
    try:
        # This would create a new case in the database
        # For now, return a success message
        
        background_tasks.add_task(log_case_upload, request)
        
        return {
            "message": "Case uploaded successfully",
            "case_title": request.case_title,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Case upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Case upload failed: {str(e)}")

@app.get("/api/v1/sections/{section_code}", tags=["Sections"])
async def get_section(
    section_code: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific law section"""
    try:
        # This would fetch section details from database
        # For now, return placeholder data
        
        return {
            "section_code": section_code,
            "title": f"Section {section_code}",
            "description": "Section description will be loaded from database",
            "status": "not_implemented"
        }
        
    except Exception as e:
        logger.error(f"Section retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Section retrieval failed: {str(e)}")

@app.get("/api/v1/analytics/search", response_model=SearchAnalytics, tags=["Analytics"])
async def get_search_analytics(
    db: Session = Depends(get_db)
):
    """Get search analytics and statistics"""
    try:
        # This would fetch analytics from database
        # For now, return placeholder data
        
        return SearchAnalytics(
            total_searches=0,
            searches_by_type={
                SearchType.SECTION_SEARCH: 0,
                SearchType.CASE_SEARCH: 0,
                SearchType.QA_SEARCH: 0,
                SearchType.SIMILARITY_SEARCH: 0
            },
            searches_by_user_type={
                UserType.JUDGE: 0,
                UserType.LAWYER: 0,
                UserType.POLICE: 0,
                UserType.STUDENT: 0,
                UserType.RESEARCHER: 0,
                UserType.GENERAL: 0
            },
            average_execution_time=0.0,
            most_common_queries=[],
            search_trends=[]
        )
        
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@app.get("/api/v1/suggestions", tags=["Search"])
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Partial search query"),
    max_suggestions: int = Query(5, ge=1, le=20, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    try:
        # This would generate suggestions based on query patterns
        # For now, return basic suggestions
        
        suggestions = [
            f"{query} murder",
            f"{query} theft",
            f"{query} assault",
            f"{query} fraud",
            f"{query} bail"
        ]
        
        return {
            "query": query,
            "suggestions": suggestions[:max_suggestions]
        }
        
    except Exception as e:
        logger.error(f"Suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")


# ============================================
# CONTACT FORM ENDPOINTS
# ============================================

@app.post("/api/v1/contact", response_model=ContactMessageResponse, tags=["Contact"])
async def submit_contact_form(
    message_data: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    """Submit a contact form message"""
    try:
        contact_service = ContactService(db)
        message = contact_service.create_message(message_data)
        
        return ContactMessageResponse(
            id=message.id,
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message,
            phone=message.phone,
            is_read=message.is_read,
            created_at=message.created_at
        )
        
    except Exception as e:
        logger.error(f"Contact form submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit contact form: {str(e)}")


@app.get("/api/v1/contact/messages", response_model=List[ContactMessageResponse], tags=["Contact"])
async def get_contact_messages(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get all contact messages (admin endpoint)"""
    try:
        contact_service = ContactService(db)
        messages = contact_service.get_all_messages(skip=skip, limit=limit)
        
        return [
            ContactMessageResponse(
                id=msg.id,
                name=msg.name,
                email=msg.email,
                subject=msg.subject,
                message=msg.message,
                phone=msg.phone,
                is_read=msg.is_read,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
    except Exception as e:
        logger.error(f"Failed to retrieve contact messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")


@app.get("/api/v1/contact/messages/{message_id}", response_model=ContactMessageResponse, tags=["Contact"])
async def get_contact_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific contact message by ID"""
    try:
        contact_service = ContactService(db)
        message = contact_service.get_message_by_id(message_id)
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return ContactMessageResponse(
            id=message.id,
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message,
            phone=message.phone,
            is_read=message.is_read,
            created_at=message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve contact message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve message: {str(e)}")


@app.patch("/api/v1/contact/messages/{message_id}/read", response_model=ContactMessageResponse, tags=["Contact"])
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Mark a contact message as read"""
    try:
        contact_service = ContactService(db)
        message = contact_service.mark_as_read(message_id)
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return ContactMessageResponse(
            id=message.id,
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message,
            phone=message.phone,
            is_read=message.is_read,
            created_at=message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark message as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")


@app.delete("/api/v1/contact/messages/{message_id}", tags=["Contact"])
async def delete_contact_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Delete a contact message"""
    try:
        contact_service = ContactService(db)
        deleted = contact_service.delete_message(message_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"message": "Contact message deleted successfully", "id": message_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete contact message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")


@app.get("/api/v1/contact/unread-count", tags=["Contact"])
async def get_unread_count(
    db: Session = Depends(get_db)
):
    """Get count of unread contact messages"""
    try:
        contact_service = ContactService(db)
        count = contact_service.get_unread_count()
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Failed to get unread count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")


# Background task functions
def log_case_upload(request: CaseUploadRequest):
    """Background task to log case upload"""
    logger.info(f"Case uploaded: {request.case_title}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
