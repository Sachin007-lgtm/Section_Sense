"""
Hugging Face API-based Search Service - Lightweight alternative to local models
Uses Hugging Face InferenceClient for embeddings instead of local sentence-transformers
"""
import logging
import os
from typing import List, Dict, Any, Optional
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Singleton pattern for InferenceClient to avoid re-initialization
_client_instance = None

@lru_cache(maxsize=1)
def get_inference_client():
    """Get or create a singleton InferenceClient instance"""
    global _client_instance
    if _client_instance is None:
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_api_key:
            try:
                from huggingface_hub import InferenceClient
                _client_instance = InferenceClient(token=hf_api_key)
                logger.info("Created singleton InferenceClient instance")
            except Exception as e:
                logger.error(f"Failed to create InferenceClient: {e}")
    return _client_instance

class HuggingFaceSearchService:
    """Search service using Hugging Face Inference API for embeddings"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.model_id = "BAAI/bge-small-en-v1.5"
        self.embedding_cache = {}  # Cache embeddings to reduce API calls
        
        if not self.hf_api_key:
            logger.warning("HUGGINGFACE_API_KEY not set - will use keyword-based search only")
            self.client = None
        else:
            try:
                self.client = get_inference_client()
                if self.client:
                    logger.info(f"Initialized search with Hugging Face API using model: {self.model_id}")
            except ImportError:
                logger.error("huggingface-hub not installed. Run: pip install huggingface-hub")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize HF InferenceClient: {e}")
                self.client = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Hugging Face using InferenceClient with caching"""
        if not self.client:
            return None
        
        # Check cache first (avoid redundant API calls)
        cache_key = text[:200]  # Use first 200 chars as key
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        import time
        
        retries = 2
        backoff = 2.0  # Increased initial backoff for model loading

        for attempt in range(retries + 1):
            try:
                # Use feature_extraction method from InferenceClient
                # This handles the new router endpoint automatically
                result = self.client.feature_extraction(
                    text=text,
                    model=self.model_id
                )
                
                # Result can be a list or numpy array
                embedding = None
                if hasattr(result, 'tolist'):
                    # Convert numpy array to list
                    embedding = result.tolist()
                elif isinstance(result, list):
                    embedding = result
                else:
                    logger.error(f"Unexpected embedding result type: {type(result)}")
                    return None
                
                # Cache the result
                self.embedding_cache[cache_key] = embedding
                
                # Limit cache size to prevent memory issues
                if len(self.embedding_cache) > 1000:
                    # Remove oldest entries (simple FIFO)
                    oldest_keys = list(self.embedding_cache.keys())[:100]
                    for key in oldest_keys:
                        del self.embedding_cache[key]
                
                return embedding

            except Exception as e:
                error_msg = str(e).lower()
                
                # Model loading - wait longer with exponential backoff
                if "loading" in error_msg or "503" in error_msg:
                    wait_time = backoff * (2 ** attempt)  # Exponential: 2s, 4s, 8s
                    logger.info(f"Model loading, waiting {wait_time}s... (attempt {attempt + 1}/{retries + 1})")
                    if attempt < retries:
                        time.sleep(wait_time)
                        continue
                
                # Rate limit - wait and retry
                if "rate limit" in error_msg or "429" in error_msg:
                    wait_time = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s... (attempt {attempt + 1}/{retries + 1})")
                    if attempt < retries:
                        time.sleep(wait_time)
                        continue
                
                # Log other errors
                logger.error(f"HF API error (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    time.sleep(backoff)
                    backoff *= 2

        logger.error("Exceeded retries while calling HF API for embeddings")
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
