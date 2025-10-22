from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Chat-related schemas
class ChatMessageSchema(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class SaveConversationRequest(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    messages: List[ChatMessageSchema] = Field(..., description="List of messages in the conversation")


class ConversationResponse(BaseModel):
    conversation_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    conversation_id: str
    title: Optional[str]
    messages: List[ChatMessageSchema]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SearchType(str, Enum):
    SECTION_SEARCH = "section_search"
    CASE_SEARCH = "case_search"
    QA_SEARCH = "qa_search"
    SIMILARITY_SEARCH = "similarity_search"

class UserType(str, Enum):
    JUDGE = "judge"
    LAWYER = "lawyer"
    POLICE = "police"
    STUDENT = "student"
    RESEARCHER = "researcher"
    GENERAL = "general"

# Request Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text", min_length=3)
    search_type: SearchType = Field(..., description="Type of search to perform")
    user_type: Optional[UserType] = Field(None, description="Type of user making the search")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class CaseUploadRequest(BaseModel):
    case_title: str = Field(..., description="Title of the case")
    case_summary: str = Field(..., description="Summary of the case")
    facts: Optional[str] = Field(None, description="Facts of the case")
    issues: Optional[str] = Field(None, description="Legal issues involved")
    court: Optional[str] = Field(None, description="Court where case was filed")
    case_type: Optional[str] = Field(None, description="Type of case")
    applicable_sections: Optional[List[str]] = Field(None, description="List of applicable law sections")

class QARequest(BaseModel):
    question: str = Field(..., description="Legal question to answer", min_length=10)
    context: Optional[str] = Field(None, description="Additional context for the question")
    user_type: Optional[UserType] = Field(None, description="Type of user asking the question")

class ExplanationRequest(BaseModel):
    section_code: str = Field(..., description="Section code to explain")
    section_text: str = Field(..., description="Full text of the section")
    context: Optional[str] = Field(None, description="Additional context for explanation")
    user_type: Optional[UserType] = Field(UserType.GENERAL, description="Type of user requesting explanation")
    explanation_style: Optional[str] = Field("simple", description="Style of explanation (simple, detailed, legal)")

# Response Schemas
class LawSectionResponse(BaseModel):
    section_code: str
    section_number: str
    title: str
    description: str
    category: str
    punishment: Optional[str]
    fine_range: Optional[str]
    imprisonment_range: Optional[str]
    bailable: Optional[str]
    cognizable: Optional[str]
    compoundable: Optional[str]
    source: Optional[str]
    last_updated: Optional[datetime]
    
    class Config:
        from_attributes = True

class LegalCaseResponse(BaseModel):
    case_number: str
    case_title: str
    petitioner: Optional[str]
    respondent: Optional[str]
    court: str
    bench: Optional[str]
    case_type: Optional[str]
    case_summary: Optional[str]
    facts: Optional[str]
    issues: Optional[str]
    arguments: Optional[str]
    judgment: Optional[str]
    verdict: Optional[str]
    filing_date: Optional[datetime]
    judgment_date: Optional[datetime]
    applicable_sections: List[LawSectionResponse] = []
    citations: List[str] = []
    
    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    query: str
    search_type: SearchType
    total_results: int
    execution_time: float
    results: List[Any]  # Can be LawSectionResponse or LegalCaseResponse
    suggestions: Optional[List[str]] = []
    filters_applied: Optional[Dict[str, Any]] = None

class QAResponse(BaseModel):
    question: str
    answer: str
    confidence_score: float
    relevant_sections: List[LawSectionResponse] = []
    relevant_cases: List[LegalCaseResponse] = []
    sources: List[str] = []
    timestamp: datetime

class ExplanationResponse(BaseModel):
    section_code: str
    section_title: str
    plain_language_explanation: str
    key_points: List[str] = []
    real_world_example: Optional[str] = None
    when_applies: Optional[str] = None
    punishment_explanation: Optional[str] = None
    related_concepts: List[str] = []
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.now)
    llm_model_used: Optional[str] = None

class CaseSimilarityResponse(BaseModel):
    input_case: LegalCaseResponse
    similar_cases: List[Dict[str, Any]] = Field(..., description="List of similar cases with similarity scores")
    similarity_analysis: Optional[str] = Field(None, description="Analysis of why cases are similar")

class AmendmentResponse(BaseModel):
    amendment_number: str
    amendment_date: datetime
    amendment_type: str
    old_text: Optional[str]
    new_text: Optional[str]
    reason: Optional[str]
    source: Optional[str]

class LawSectionDetailResponse(LawSectionResponse):
    amendments: List[AmendmentResponse] = []
    related_cases: List[LegalCaseResponse] = []
    category_description: Optional[str] = None

# Analytics Schemas
class SearchAnalytics(BaseModel):
    total_searches: int
    searches_by_type: Dict[SearchType, int]
    searches_by_user_type: Dict[UserType, int]
    average_execution_time: float
    most_common_queries: List[Dict[str, Any]]
    search_trends: List[Dict[str, Any]]

class SystemHealth(BaseModel):
    status: str
    database_connected: bool
    search_index_healthy: bool
    total_sections: int
    total_cases: int
    last_data_update: Optional[datetime]
    system_uptime: Optional[str]

# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationError(BaseModel):
    field: str
    message: str
    value: Optional[Any] = None

class ValidationErrorResponse(BaseModel):
    error: str = "Validation Error"
    message: str = "One or more validation errors occurred"
    details: List[ValidationError]
    timestamp: datetime = Field(default_factory=datetime.now)
