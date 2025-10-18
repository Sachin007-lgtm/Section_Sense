from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

# Association table for many-to-many relationships
case_section_association = Table(
    'case_section_association',
    Base.metadata,
    Column('case_id', Integer, ForeignKey('legal_cases.id')),
    Column('section_id', Integer, ForeignKey('law_sections.id'))
)

class LawSection(Base):
    """Model for law sections (e.g., IPC sections)"""
    __tablename__ = 'law_sections'
    
    id = Column(Integer, primary_key=True, index=True)
    section_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "IPC 302"
    section_number = Column(String(20), nullable=False)  # e.g., "302"
    title = Column(String(500), nullable=False)  # e.g., "Punishment for Murder"
    description = Column(Text, nullable=False)  # Full section text
    category = Column(String(100), nullable=False)  # e.g., "Offences Affecting Human Body"
    punishment = Column(Text)  # Applicable punishments
    fine_range = Column(String(100))  # Fine amount range
    imprisonment_range = Column(String(100))  # Imprisonment range
    bailable = Column(String(10))  # "Bailable" or "Non-bailable"
    cognizable = Column(String(10))  # "Cognizable" or "Non-cognizable"
    compoundable = Column(String(10))  # "Compoundable" or "Non-compoundable"
    
    # Metadata
    source = Column(String(500))  # Source website/URL
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    related_cases = relationship("LegalCase", secondary=case_section_association, back_populates="applicable_sections")
    amendments = relationship("LawAmendment", back_populates="section")
    
    def __repr__(self):
        return f"<LawSection(section_code='{self.section_code}', title='{self.title}')>"

class LegalCase(Base):
    """Model for legal cases and judgments"""
    __tablename__ = 'legal_cases'
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True, nullable=False)
    case_title = Column(String(500), nullable=False)
    petitioner = Column(String(200))
    respondent = Column(String(200))
    court = Column(String(200), nullable=False)  # e.g., "Supreme Court of India"
    bench = Column(String(100))  # e.g., "2 Judge Bench"
    case_type = Column(String(100))  # e.g., "Criminal Appeal", "Writ Petition"
    
    # Case details
    case_summary = Column(Text)
    facts = Column(Text)
    issues = Column(Text)
    arguments = Column(Text)
    judgment = Column(Text)
    verdict = Column(String(100))  # e.g., "Allowed", "Dismissed", "Partly Allowed"
    
    # Dates
    filing_date = Column(DateTime)
    judgment_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    applicable_sections = relationship("LawSection", secondary=case_section_association, back_populates="related_cases")
    citations = relationship("CaseCitation", back_populates="case")
    
    def __repr__(self):
        return f"<LegalCase(case_number='{self.case_number}', title='{self.title}')>"

class CaseCitation(Base):
    """Model for case citations and references"""
    __tablename__ = 'case_citations'
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey('legal_cases.id'), nullable=False)
    citation_text = Column(String(200), nullable=False)  # e.g., "AIR 1973 SC 947"
    citation_type = Column(String(50))  # e.g., "AIR", "SCC", "Cri LJ"
    year = Column(Integer)
    volume = Column(String(20))
    page = Column(String(20))
    
    # Relationships
    case = relationship("LegalCase", back_populates="citations")
    
    def __repr__(self):
        return f"<CaseCitation(citation='{self.citation_text}')>"

class LawAmendment(Base):
    """Model for tracking amendments to law sections"""
    __tablename__ = 'law_amendments'
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey('law_sections.id'), nullable=False)
    amendment_number = Column(String(100))
    amendment_date = Column(DateTime)
    amendment_type = Column(String(100))  # e.g., "Insertion", "Substitution", "Deletion"
    old_text = Column(Text)
    new_text = Column(Text)
    reason = Column(Text)
    source = Column(String(500))  # Official gazette or notification
    
    # Relationships
    section = relationship("LawSection", back_populates="amendments")
    
    def __repr__(self):
        return f"<LawAmendment(section_id={self.section_id}, type='{self.amendment_type}')>"

class SearchQuery(Base):
    """Model for tracking search queries for analytics"""
    __tablename__ = 'search_queries'
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    user_type = Column(String(50))  # e.g., "Judge", "Lawyer", "Police", "Student"
    search_type = Column(String(50))  # e.g., "Section Search", "Case Search", "Q&A"
    results_count = Column(Integer)
    execution_time = Column(Float)  # in seconds
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String(45))  # IPv4 or IPv6
    
    def __repr__(self):
        return f"<SearchQuery(query='{self.query_text[:50]}...', timestamp='{self.timestamp}')>"

class CaseSimilarity(Base):
    """Model for storing case similarity scores"""
    __tablename__ = 'case_similarities'
    
    id = Column(Integer, primary_key=True, index=True)
    case1_id = Column(Integer, ForeignKey('legal_cases.id'), nullable=False)
    case2_id = Column(Integer, ForeignKey('legal_cases.id'), nullable=False)
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    similarity_type = Column(String(50))  # e.g., "Text Similarity", "Legal Issue Similarity"
    created_at = Column(DateTime, default=func.now())
    
    # Ensure unique pairs
    __table_args__ = (
        Index('unique_case_pair', 'case1_id', 'case2_id', unique=True),
    )
    
    def __repr__(self):
        return f"<CaseSimilarity(case1={self.case1_id}, case2={self.case2_id}, score={self.similarity_score})>"

# Create indexes for better performance
Index('idx_law_sections_category', LawSection.category)
Index('idx_law_sections_section_number', LawSection.section_number)
Index('idx_legal_cases_court', LegalCase.court)
Index('idx_legal_cases_judgment_date', LegalCase.judgment_date)
Index('idx_search_queries_timestamp', SearchQuery.timestamp)
