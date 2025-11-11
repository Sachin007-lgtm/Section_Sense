"""
Universal Database Search Service - Works with both SQLite and PostgreSQL
Automatically detects the database type and uses appropriate queries
"""
import logging
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database detection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./criminal_law_kb.db")
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Import appropriate database module
if IS_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
else:
    import sqlite3

# Import HuggingFace-based search service
from app.services.hf_search_service import HuggingFaceSearchService

logger = logging.getLogger(__name__)

class UniversalSearchService:
    """Universal legal search service that works with both SQLite and PostgreSQL"""
    
    def __init__(self, db_path_or_url: Optional[str] = None):
        """
        Initialize search service
        Args:
            db_path_or_url: Database path (SQLite) or connection URL (PostgreSQL)
                           If None, uses DATABASE_URL from environment
        """
        self.database_url = db_path_or_url or DATABASE_URL
        self.is_postgres = self.database_url.startswith("postgresql")
        self.hf_service = HuggingFaceSearchService()
        
        logger.info(f"Initialized search service with {'PostgreSQL' if self.is_postgres else 'SQLite'}")
        logger.info("Using Hugging Face API for semantic search")
    
    def _get_connection(self):
        """Get database connection based on database type"""
        if self.is_postgres:
            return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        else:
            conn = sqlite3.connect(self.database_url.replace("sqlite:///./", "").replace("sqlite:///", ""))
            conn.row_factory = sqlite3.Row
            return conn
    
    def _get_param_placeholder(self, index: int = 0) -> str:
        """Get parameter placeholder for SQL query"""
        if self.is_postgres:
            return f"%s"  # PostgreSQL uses %s
        else:
            return "?"  # SQLite uses ?
    
    def _get_like_operator(self) -> str:
        """Get case-insensitive LIKE operator"""
        return "ILIKE" if self.is_postgres else "LIKE"
    
    def _expand_query(self, query: str) -> str:
        """Expand query with legal synonyms and related terms"""
        query_lower = query.lower()
        
        # Legal terminology synonyms
        expansions = {
            # Domestic/Family violence
            'domestic violence': 'domestic violence cruelty wife husband woman',
            'domestic abuse': 'domestic violence cruelty wife husband woman',
            'wife beating': 'cruelty domestic violence husband woman',
            'marital violence': 'cruelty domestic violence husband wife',
            'dowry': 'dowry cruelty harassment woman',
            
            # Sexual offenses
            'rape': 'rape sexual assault intercourse',
            'sexual assault': 'sexual assault rape intercourse',
            'sexual harassment': 'sexual harassment assault',
            'molestation': 'molestation sexual assault',
            
            # Cyber/Technology crimes
            'cybercrime': 'cybercrime electronic computer digital online document record',
            'cyber crime': 'cybercrime electronic computer digital online document record',
            'hacking': 'hacking electronic computer unauthorized access',
            'online fraud': 'fraud electronic computer cheating online',
            'digital fraud': 'fraud electronic computer cheating digital',
            'phishing': 'phishing fraud cheating electronic',
            'identity theft': 'identity theft fraud cheating forgery electronic',
            'data theft': 'theft electronic computer document record',
            'computer crime': 'computer electronic digital document record',
            
            # Property crimes
            'kidnapping': 'kidnapping abduction',
            'abduction': 'abduction kidnapping',
            'murder': 'murder culpable homicide death killing',
            'theft': 'theft stealing robbery extortion',
            'robbery': 'robbery theft dacoity extortion',
            'burglary': 'burglary theft house breaking',
            'extortion': 'extortion robbery threat',
            
            # Financial crimes
            'fraud': 'fraud cheating forgery deception',
            'cheating': 'cheating fraud deception forgery',
            'forgery': 'forgery fraud cheating document',
            'embezzlement': 'embezzlement theft cheating fraud',
            'bribery': 'bribery corruption gratification',
            'corruption': 'corruption bribery gratification',
            
            # Other crimes
            'assault': 'assault hurt injury violence',
            'defamation': 'defamation reputation harm',
            'harassment': 'harassment intimidation threat',
        }
        
        # Check if query matches any expansion patterns
        for key, expanded in expansions.items():
            if key in query_lower:
                logger.info(f"Query expansion: '{query}' → '{expanded}'")
                return expanded
        
        return query
    
    def search_sections(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                       max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for law sections with semantic ranking"""
        try:
            # Expand query with legal synonyms
            expanded_query = self._expand_query(query)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build the base query
            sql_query = """
            SELECT 
                id, section_code, section_number, title, description,
                category, punishment, source, last_updated
            FROM law_sections 
            WHERE 1=1
            """
            
            params = []
            like_op = self._get_like_operator()
            param_placeholder = self._get_param_placeholder()
            
            # Filter out stop words
            stop_words = {'and', 'or', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 
                         'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'has', 'have', 
                         'that', 'this', 'by', 'from', 'as', 'it', 'its'}
            
            # Add search conditions - use expanded query for DB search
            if expanded_query.strip():
                search_terms = [term for term in expanded_query.strip().lower().split() 
                              if term not in stop_words and len(term) > 2]
                
                if not search_terms:
                    # If all were stop words, use original query
                    search_terms = query.strip().split()
                
                search_conditions = []
                
                for term in search_terms:
                    if term.isdigit():
                        # Search for section number
                        search_conditions.append(f"section_number {like_op} {param_placeholder}")
                        params.append(f"%{term}%")
                    else:
                        # Search in title, description, and category
                        if self.is_postgres:
                            search_conditions.append(f"""
                                (title {like_op} {param_placeholder} OR 
                                 description {like_op} {param_placeholder} OR
                                 category {like_op} {param_placeholder})
                            """)
                        else:
                            search_conditions.append(f"""
                                (LOWER(title) {like_op} LOWER({param_placeholder}) OR 
                                 LOWER(description) {like_op} LOWER({param_placeholder}) OR
                                 LOWER(category) {like_op} LOWER({param_placeholder}))
                            """)
                        search_term = f"%{term}%"
                        params.extend([search_term, search_term, search_term])
                
                if search_conditions:
                    sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            
            # Add filters
            if filters:
                if 'category' in filters and filters['category']:
                    sql_query += f" AND category = {param_placeholder}"
                    params.append(filters['category'])
                
                if 'section_number' in filters and filters['section_number']:
                    sql_query += f" AND section_number = {param_placeholder}"
                    params.append(filters['section_number'])
                
                if 'bailable' in filters and filters['bailable']:
                    sql_query += f" AND bailable = {param_placeholder}"
                    params.append(filters['bailable'])
                
                if 'cognizable' in filters and filters['cognizable']:
                    sql_query += f" AND cognizable = {param_placeholder}"
                    params.append(filters['cognizable'])
            
            # Execute query
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            
            # Convert rows to list of dicts
            sections = []
            for row in rows:
                sections.append(dict(row))
            
            conn.close()
            
            # Apply semantic ranking using HuggingFace API
            if sections:
                sections = self.hf_service.rank_by_semantic_similarity(sections, query)
            
            # Limit results
            sections = sections[:max_results]
            
            # Log results for debugging
            if sections:
                logger.info(f"Search '{query}' returned {len(sections)} results")
                logger.info(f"Top 5 results: {[s.get('section_code', 'unknown') for s in sections[:5]]}")
            
            return sections
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _keyword_rank(self, sections: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank sections by keyword relevance (fallback when ML not available)"""
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for section in sections:
            score = 0
            title = section.get('title', '').lower()
            description = section.get('description', '').lower()
            category = section.get('category', '').lower()
            
            # Exact title match gets highest score
            if query_lower in title:
                score += 50
            
            # Query appears in title
            if query_lower.replace(' ', '') in title.replace(' ', ''):
                score += 30
            
            # Count matching terms
            title_terms = set(title.split())
            desc_terms = set(description.split())
            
            matching_terms = query_terms & title_terms
            score += len(matching_terms) * 10
            
            # Query in description
            if query_lower in description:
                score += 15
            
            # Individual terms in description
            desc_matches = query_terms & desc_terms
            score += len(desc_matches) * 5
            
            # Category match
            if query_lower in category:
                score += 8
            
            section['relevance_score'] = score
        
        # Sort by relevance score descending
        ranked_sections = sorted(sections, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Log top results
        logger.info(f"Top 5 keyword-ranked results:")
        for section in ranked_sections[:5]:
            logger.info(f"  {section.get('section_code')}: {section.get('title')[:50]}... (score: {section.get('relevance_score')})")
        
        return ranked_sections
    

    
    def get_section_by_code(self, section_code: str) -> Optional[Dict[str, Any]]:
        """Get a specific section by its code"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            param_placeholder = self._get_param_placeholder()
            query = f"""
            SELECT 
                id, section_code, section_number, title, description,
                category, punishment, bailable, cognizable, compoundable,
                fine_range, imprisonment_range, source, last_updated
            FROM law_sections 
            WHERE section_code = {param_placeholder}
            """
            
            cursor.execute(query, (section_code,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get section {section_code}: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT DISTINCT category FROM law_sections ORDER BY category"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            return [row['category'] if isinstance(row, dict) else row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on query"""
        try:
            if not query or len(query) < 2:
                return []
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            like_op = self._get_like_operator()
            param_placeholder = self._get_param_placeholder()
            
            # Get suggestions from section titles and codes
            if self.is_postgres:
                sql_query = f"""
                SELECT DISTINCT section_code, title 
                FROM law_sections 
                WHERE section_code {like_op} {param_placeholder} 
                   OR title {like_op} {param_placeholder}
                LIMIT 5
                """
            else:
                sql_query = f"""
                SELECT DISTINCT section_code, title 
                FROM law_sections 
                WHERE LOWER(section_code) {like_op} LOWER({param_placeholder}) 
                   OR LOWER(title) {like_op} LOWER({param_placeholder})
                LIMIT 5
                """
            
            search_term = f"%{query}%"
            cursor.execute(sql_query, (search_term, search_term))
            rows = cursor.fetchall()
            conn.close()
            
            suggestions = []
            for row in rows:
                row_dict = dict(row)
                suggestion = f"{row_dict['section_code']}: {row_dict['title'][:50]}"
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

# For backward compatibility
SQLiteSearchService = UniversalSearchService
