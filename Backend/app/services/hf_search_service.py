"""
Hugging Face API-based Search Service - Lightweight alternative to local models
Uses Hugging Face Inference API for embeddings instead of local sentence-transformers
"""
import logging
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class HuggingFaceSearchService:
    """Search service using Hugging Face Inference API for embeddings"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {"Authorization": f"Bearer {self.hf_api_key}"} if self.hf_api_key else {}
        
        if not self.hf_api_key:
            logger.warning("HUGGINGFACE_API_KEY not set - will use keyword-based search only")
        else:
            logger.info("Initialized search with Hugging Face API")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Hugging Face API"""
        if not self.hf_api_key:
            return None
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HF API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get embedding from HF API: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def rank_by_semantic_similarity(self, sections: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank sections using Hugging Face API embeddings"""
        if not self.hf_api_key or not sections:
            return self.keyword_rank(sections, query)
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                logger.warning("Failed to get query embedding, falling back to keyword search")
                return self.keyword_rank(sections, query)
            
            # Get embeddings for each section (batch processing would be better)
            for section in sections:
                text = f"{section.get('title', '')} {section.get('description', '')[:500]}"
                section_embedding = self.get_embedding(text)
                
                if section_embedding:
                    similarity = self.cosine_similarity(query_embedding, section_embedding)
                    section['similarity_score'] = similarity
                    section['relevance_score'] = similarity
                else:
                    section['similarity_score'] = 0.0
                    section['relevance_score'] = 0.0
            
            # Sort by similarity
            ranked_sections = sorted(sections, key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            logger.info(f"Top 5 semantically ranked results (HF API):")
            for section in ranked_sections[:5]:
                logger.info(f"  {section.get('section_code')}: {section.get('title')[:50]}... (score: {section.get('similarity_score', 0):.3f})")
            
            return ranked_sections
            
        except Exception as e:
            logger.error(f"Semantic ranking with HF API failed: {e}")
            return self.keyword_rank(sections, query)
    
    def keyword_rank(self, sections: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Fallback keyword-based ranking"""
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for section in sections:
            score = 0
            title = section.get('title', '').lower()
            description = section.get('description', '').lower()
            category = section.get('category', '').lower()
            
            # Exact title match
            if query_lower in title:
                score += 50
            
            # Query in title (no spaces)
            if query_lower.replace(' ', '') in title.replace(' ', ''):
                score += 30
            
            # Matching terms in title
            title_terms = set(title.split())
            matching_terms = query_terms & title_terms
            score += len(matching_terms) * 10
            
            # Query in description
            if query_lower in description:
                score += 15
            
            # Matching terms in description
            desc_terms = set(description.split())
            desc_matches = query_terms & desc_terms
            score += len(desc_matches) * 5
            
            # Category match
            if query_lower in category:
                score += 8
            
            section['relevance_score'] = score
        
        # Sort by relevance
        ranked_sections = sorted(sections, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Top 5 keyword-ranked results:")
        for section in ranked_sections[:5]:
            logger.info(f"  {section.get('section_code')}: {section.get('title')[:50]}... (score: {section.get('relevance_score')})")
        
        return ranked_sections
