"""
Schemas package for Pydantic models
"""

# Re-export main schemas so "from app.schemas import X" works
from .main_schemas import (
    SearchRequest, SearchResult, CaseUploadRequest, QARequest, QAResponse,
    SearchType, UserType, SystemHealth, SearchAnalytics, ExplanationRequest,
    ExplanationResponse, ChatMessageSchema, SaveConversationRequest,
    ConversationResponse, ConversationDetailResponse, LawSectionResponse,
    LegalCaseResponse
)

__all__ = [
    "SearchRequest", "SearchResult", "CaseUploadRequest", "QARequest", "QAResponse",
    "ExplanationRequest", "ExplanationResponse", "SearchType", "UserType",
    "SystemHealth", "SearchAnalytics", "ChatMessageSchema", "SaveConversationRequest",
    "ConversationResponse", "ConversationDetailResponse", "LawSectionResponse",
    "LegalCaseResponse"
]