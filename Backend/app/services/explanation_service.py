import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Import for different LLM providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# For local Ollama
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from app.schemas import ExplanationRequest, ExplanationResponse, UserType

logger = logging.getLogger(__name__)

class LegalExplanationService:
    """Service for generating plain-language explanations of legal sections using LLMs"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.preferred_provider = os.getenv("LLM_PROVIDER", "openai")  # openai, groq, ollama
        
    def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """Generate a plain-language explanation for a legal section"""
        try:
            # Choose LLM provider based on availability and preference
            if self.preferred_provider == "groq" and GROQ_AVAILABLE and self.groq_api_key:
                explanation_data = self._generate_with_groq(request)
            elif self.preferred_provider == "ollama" and REQUESTS_AVAILABLE:
                explanation_data = self._generate_with_ollama(request)
            elif OPENAI_AVAILABLE and self.openai_api_key:
                explanation_data = self._generate_with_openai(request)
            else:
                # Fallback to a simple rule-based explanation
                explanation_data = self._generate_fallback_explanation(request)
            
            return ExplanationResponse(**explanation_data)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            # Return a fallback explanation
            return self._generate_error_fallback(request)
    
    def _generate_with_openai(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate explanation using OpenAI GPT"""
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = self._build_prompt(request)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(request.user_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            explanation_text = response.choices[0].message.content
            return self._parse_explanation_response(explanation_text, request, "openai-gpt-3.5-turbo")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_with_groq(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate explanation using Groq"""
        try:
            client = groq.Groq(api_key=self.groq_api_key)
            
            prompt = self._build_prompt(request)
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated to current model
                messages=[
                    {"role": "system", "content": self._get_system_prompt(request.user_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            explanation_text = response.choices[0].message.content
            return self._parse_explanation_response(explanation_text, request, "groq-llama-3.1")
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def _generate_with_ollama(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate explanation using local Ollama"""
        try:
            prompt = self._build_prompt(request)
            system_prompt = self._get_system_prompt(request.user_type)
            
            payload = {
                "model": "llama2",  # or another model you have installed
                "prompt": f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            explanation_text = response.json().get("response", "")
            return self._parse_explanation_response(explanation_text, request, "ollama-llama2")
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def _build_prompt(self, request: ExplanationRequest) -> str:
        """Build the prompt for LLM based on the request"""
        prompt = f"""
Please explain the following legal section in simple, plain language that anyone can understand:

**Section Code:** {request.section_code}
**Section Text:** {request.section_text}

Please provide:
1. A clear, simple explanation of what this section means
2. 3-5 key points about this section
3. A real-world example of when this section would apply
4. When this section applies (circumstances)
5. If there are punishments, explain them in simple terms
6. Related legal concepts someone should know

Make the explanation accessible to a {request.user_type or 'general'} audience.
"""
        
        if request.context:
            prompt += f"\n**Additional Context:** {request.context}"
        
        prompt += """

Format your response as a JSON object with the following structure:
{
    "plain_language_explanation": "Main explanation in simple terms",
    "key_points": ["point 1", "point 2", "point 3"],
    "real_world_example": "Example scenario",
    "when_applies": "Circumstances when this applies",
    "punishment_explanation": "Simple explanation of punishments if any",
    "related_concepts": ["concept 1", "concept 2"]
}
"""
        return prompt
    
    def _get_system_prompt(self, user_type: Optional[UserType]) -> str:
        """Get system prompt based on user type"""
        base_prompt = """You are a legal expert who specializes in explaining complex legal sections in simple, plain language. Your goal is to make legal concepts accessible to everyone."""
        
        if user_type == UserType.STUDENT:
            return base_prompt + " Focus on educational aspects and provide learning-friendly explanations."
        elif user_type == UserType.GENERAL:
            return base_prompt + " Use everyday language and avoid legal jargon. Focus on practical implications."
        elif user_type == UserType.LAWYER:
            return base_prompt + " You can use some legal terminology but still keep explanations clear and practical."
        else:
            return base_prompt + " Adapt your explanation to be clear and practical for the intended audience."
    
    def _parse_explanation_response(self, response_text: str, request: ExplanationRequest, model_name: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            # Try to extract JSON from the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                parsed_data = json.loads(json_str)
            else:
                # If no JSON found, create a simple structure
                parsed_data = {
                    "plain_language_explanation": response_text,
                    "key_points": [],
                    "real_world_example": None,
                    "when_applies": None,
                    "punishment_explanation": None,
                    "related_concepts": []
                }
            
            return {
                "section_code": request.section_code,
                "section_title": f"Section {request.section_code}",
                "plain_language_explanation": parsed_data.get("plain_language_explanation", response_text),
                "key_points": parsed_data.get("key_points", []),
                "real_world_example": parsed_data.get("real_world_example"),
                "when_applies": parsed_data.get("when_applies"),
                "punishment_explanation": parsed_data.get("punishment_explanation"),
                "related_concepts": parsed_data.get("related_concepts", []),
                "confidence_score": 0.8,
                "generated_at": datetime.now(),
                "llm_model_used": model_name
            }
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using text as explanation")
            return {
                "section_code": request.section_code,
                "section_title": f"Section {request.section_code}",
                "plain_language_explanation": response_text,
                "key_points": [],
                "real_world_example": None,
                "when_applies": None,
                "punishment_explanation": None,
                "related_concepts": [],
                "confidence_score": 0.6,
                "generated_at": datetime.now(),
                "llm_model_used": model_name
            }
    
    def _generate_fallback_explanation(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate a simple rule-based explanation when LLM is not available"""
        
        section_text_lower = request.section_text.lower()
        section_code = request.section_code.lower()
        
        # Enhanced pattern matching for common legal concepts
        key_points = []
        punishment_explanation = None
        plain_explanation = ""
        real_world_example = ""
        when_applies = ""
        related_concepts = []
        
        # Murder and homicide
        if "murder" in section_text_lower or "death" in section_text_lower or "302" in section_code:
            key_points = [
                "This section deals with serious crimes involving intentional killing",
                "Intent to cause death is a key factor",
                "One of the most serious offenses in criminal law",
                "Carries the highest penalties including life imprisonment or death"
            ]
            plain_explanation = f"Section {request.section_code} deals with murder - the intentional killing of another person. This is considered one of the most serious crimes."
            real_world_example = "If someone deliberately kills another person during a fight or plans a murder, this section would apply."
            when_applies = "When someone intentionally causes death of another person"
            punishment_explanation = "Death penalty or life imprisonment, along with possible fines"
            related_concepts = ["Intent", "Homicide", "Life imprisonment", "Death penalty"]
            
        # Theft and stealing
        elif "theft" in section_text_lower or "stealing" in section_text_lower or "379" in section_code:
            key_points = [
                "This section covers taking someone else's property without permission",
                "Intent to permanently deprive the owner is required",
                "The value of stolen items affects the severity of punishment",
                "No force or threats are involved (unlike robbery)"
            ]
            plain_explanation = f"Section {request.section_code} defines theft - taking someone's property without their consent with the intention to keep it."
            real_world_example = "Stealing money from someone's wallet, taking a bicycle without permission, or shoplifting from a store."
            when_applies = "When someone dishonestly takes movable property belonging to another person"
            punishment_explanation = "Imprisonment up to 3 years or fine or both, depending on the value"
            related_concepts = ["Dishonest intention", "Movable property", "Consent", "Robbery"]
            
        # Assault and hurt
        elif "assault" in section_text_lower or "hurt" in section_text_lower or any(x in section_code for x in ["320", "322", "323", "325"]):
            key_points = [
                "This section deals with causing physical harm to another person",
                "Includes both simple and grievous hurt",
                "Intent to cause hurt or knowledge that actions may cause hurt",
                "Physical contact or bodily pain is involved"
            ]
            plain_explanation = f"Section {request.section_code} covers causing hurt or injury to another person's body."
            real_world_example = "Hitting someone in a fight, causing injuries in an accident through negligence, or attacking someone."
            when_applies = "When someone voluntarily causes bodily pain, disease or infirmity to another person"
            punishment_explanation = "Imprisonment up to 1-3 years and/or fine, more for grievous hurt"
            related_concepts = ["Bodily harm", "Grievous hurt", "Simple hurt", "Assault"]
            
        # Fraud and cheating  
        elif "cheat" in section_text_lower or "fraud" in section_text_lower or "420" in section_code:
            key_points = [
                "This section covers deceiving someone to gain unfairly",
                "Involves dishonest intention and deception",
                "Victim must be induced to do or not do something",
                "Financial or property-related benefits are usually involved"
            ]
            plain_explanation = f"Section {request.section_code} deals with cheating - deceiving someone to make them act in a way that harms them."
            real_world_example = "Selling fake products as genuine, using false documents to get loans, or online scams."
            when_applies = "When someone deceives another person to dishonestly induce them to deliver property or do something"
            punishment_explanation = "Imprisonment up to 7 years and/or fine"
            related_concepts = ["Deception", "Dishonest intention", "Property", "Fraud"]
            
        # Rape and sexual offenses
        elif "rape" in section_text_lower or any(x in section_code for x in ["375", "376"]):
            key_points = [
                "This section deals with serious sexual offenses",
                "Consent is the central issue",
                "Severe punishments reflect the gravity of the offense",
                "Protection of women and vulnerable persons"
            ]
            plain_explanation = f"Section {request.section_code} defines and punishes sexual assault and rape - serious crimes against women."
            real_world_example = "Any non-consensual sexual act or assault on a woman."
            when_applies = "When sexual assault occurs without consent or against a minor"
            punishment_explanation = "Rigorous imprisonment for minimum 7 years, can extend to life imprisonment"
            related_concepts = ["Consent", "Sexual assault", "Women's protection", "Rigorous imprisonment"]
            
        # Robbery and dacoity
        elif "robb" in section_text_lower or "daco" in section_text_lower or any(x in section_code for x in ["390", "395"]):
            key_points = [
                "This section covers theft involving force or threat",
                "More serious than simple theft due to violence/intimidation",
                "Can involve groups of people (dacoity)",
                "Victim's safety is endangered"
            ]
            plain_explanation = f"Section {request.section_code} deals with robbery - theft involving force, violence or threats."
            real_world_example = "Snatching a purse after pushing someone, bank robbery, highway robbery by gangs."
            when_applies = "When theft is committed with force, violence or threat of violence"
            punishment_explanation = "Rigorous imprisonment up to 10 years and fine, life imprisonment for dacoity"
            related_concepts = ["Force", "Violence", "Theft", "Dacoity", "Gang crime"]
            
        # Kidnapping and abduction
        elif "kidnap" in section_text_lower or "abduct" in section_text_lower or any(x in section_code for x in ["359", "361", "363"]):
            key_points = [
                "This section covers forcibly taking someone away",
                "Involves restricting someone's freedom of movement",
                "Different penalties for kidnapping adults vs children",
                "Often linked to other serious crimes"
            ]
            plain_explanation = f"Section {request.section_code} deals with kidnapping or abduction - forcibly taking someone away against their will."
            real_world_example = "Taking a child away from parents, forcing someone into a car, holding someone captive."
            when_applies = "When someone is taken away from their lawful guardian or against their will"
            punishment_explanation = "Imprisonment up to 7 years and fine, more for kidnapping children"
            related_concepts = ["Abduction", "Lawful guardian", "Minor", "Captivity"]
            
        # Defamation
        elif "defam" in section_text_lower or any(x in section_code for x in ["499", "500"]):
            key_points = [
                "This section protects people's reputation",
                "Covers false statements that harm someone's image",
                "Can be spoken (slander) or written (libel)",
                "Truth and public interest are defenses"
            ]
            plain_explanation = f"Section {request.section_code} deals with defamation - making false statements that damage someone's reputation."
            real_world_example = "Spreading false rumors about someone, posting lies on social media, publishing false news about a person."
            when_applies = "When false statements are made that harm someone's reputation in public"
            punishment_explanation = "Simple imprisonment up to 2 years or fine or both"
            related_concepts = ["Reputation", "False statement", "Public opinion", "Libel", "Slander"]
            
        # Default fallback - but make it more specific to the section
        else:
            # Extract section number for more specific response
            section_num = ''.join(filter(str.isdigit, request.section_code))
            key_points = [
                f"Section {request.section_code} is a specific legal provision in criminal law",
                "It defines certain prohibited conduct or establishes legal procedures",
                "Violations can result in criminal penalties",
                "Part of the comprehensive framework of criminal justice"
            ]
            plain_explanation = f"Section {request.section_code} is a legal provision that defines specific criminal conduct or legal procedures. While the exact details require legal expertise, this section is part of the criminal law framework designed to maintain order and justice in society."
            real_world_example = "This section would apply in specific legal situations as defined by the law."
            when_applies = f"When the specific circumstances outlined in Section {request.section_code} are present"
            punishment_explanation = "Penalties as prescribed under this section of the law"
            related_concepts = ["Criminal law", "Legal procedures", "Justice system", "Law enforcement"]

        return {
            "section_code": request.section_code,
            "section_title": f"Section {request.section_code}",
            "plain_language_explanation": plain_explanation,
            "key_points": key_points,
            "real_world_example": real_world_example,
            "when_applies": when_applies,
            "punishment_explanation": punishment_explanation,
            "related_concepts": related_concepts,
            "confidence_score": 0.4,
            "generated_at": datetime.now(),
            "llm_model_used": "rule-based-fallback"
        }
    
    def _generate_error_fallback(self, request: ExplanationRequest) -> ExplanationResponse:
        """Generate a basic response when all other methods fail"""
        return ExplanationResponse(
            section_code=request.section_code,
            section_title=f"Section {request.section_code}",
            plain_language_explanation="I apologize, but I'm unable to generate a detailed explanation at this moment. This section is part of the legal framework and defines specific rules or prohibitions.",
            key_points=["This is a legal provision", "It defines specific conduct or rules", "Compliance is required under law"],
            real_world_example=None,
            when_applies="When the circumstances described in the section are present",
            punishment_explanation=None,
            related_concepts=["Legal compliance", "Rule of law"],
            confidence_score=0.2,
            generated_at=datetime.now(),
            llm_model_used="error-fallback"
        )