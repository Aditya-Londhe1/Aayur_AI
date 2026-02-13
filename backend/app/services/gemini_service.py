"""
Gemini AI Conversation Service
Handles natural language conversations for health assessment
"""

import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from datetime import datetime
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiConversationService:
    """
    Manage conversations with Gemini AI for health assessment
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in settings")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # System prompt for Ayurvedic health assistant
        self.system_prompt = """You are an empathetic Ayurvedic health assistant for AayurAI.

Your role:
- Have natural, caring conversations about health concerns
- Ask relevant follow-up questions about symptoms
- Collect information: symptoms, duration, severity, patient details
- Be culturally sensitive and supportive
- Keep responses concise (2-3 sentences)
- Focus on understanding the patient's condition

Guidelines:
- Start by asking what health concerns they have
- Ask about symptom duration and severity
- Ask about age, gender if relevant
- Be warm and reassuring
- Don't diagnose - just gather information
- After collecting enough info, suggest they proceed with assessment

Remember: You're gathering information for an AI-powered Ayurvedic diagnosis system."""
        
        # Conversation sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, session_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Start a new conversation session
        
        Args:
            session_id: Unique session identifier
            language: User's preferred language
            
        Returns:
            Session info with initial greeting
        """
        # Create new session
        self.sessions[session_id] = {
            "id": session_id,
            "language": language,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "extracted_info": {
                "symptoms": [],
                "patient_info": {},
                "ready_for_assessment": False
            }
        }
        
        # Language names for better prompting
        language_names = {
            "en": "English",
            "hi": "Hindi (हिंदी)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "bn": "Bengali (বাংলা)",
            "mr": "Marathi (मराठी)",
            "gu": "Gujarati (ગુજરાતી)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "ml": "Malayalam (മലയാളം)",
            "pa": "Punjabi (ਪੰਜਾਬੀ)",
            "or": "Odia (ଓଡ଼ିଆ)"
        }
        
        language_name = language_names.get(language, "English")
        
        # Generate initial greeting with language instruction
        greeting_prompt = f"""{self.system_prompt}

CRITICAL LANGUAGE INSTRUCTION:
- You MUST respond ONLY in {language_name}
- Do NOT use English or any other language
- Write your entire response in {language_name} script
- The user speaks {language_name}, so communicate in {language_name}
- If you don't know {language_name}, use simple words but stay in {language_name}

Task: Generate a warm, friendly greeting in {language_name} asking how you can help with their health concerns. Keep it to 1-2 sentences. Write ONLY in {language_name}."""
        
        try:
            # Use generation config for better control
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 200,
            }
            
            response = self.model.generate_content(
                greeting_prompt,
                generation_config=generation_config
            )
            greeting = response.text
            
            # Store in session
            self.sessions[session_id]["messages"].append({
                "role": "assistant",
                "content": greeting,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Started session {session_id} in language {language} ({language_name})")
            
            return {
                "session_id": session_id,
                "message": greeting,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            # Fallback greetings in different languages
            fallback_greetings = {
                "en": "Hello! I'm here to help you with your health concerns. What brings you here today?",
                "hi": "नमस्ते! मैं आपकी स्वास्थ्य समस्याओं में मदद के लिए यहाँ हूँ। आज आप यहाँ क्यों आए हैं?",
                "ta": "வணக்கம்! உங்கள் உடல்நல கவலைகளுக்கு உதவ நான் இங்கே இருக்கிறேன். இன்று உங்களை இங்கு என்ன கொண்டு வந்தது?",
                "te": "నమస్కారం! మీ ఆరోగ్య సమస్యలకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. ఈరోజు మిమ్మల్ని ఇక్కడికి తీసుకొచ్చింది ఏమిటి?",
                "bn": "নমস্কার! আমি আপনার স্বাস্থ্য সমস্যায় সাহায্য করতে এখানে আছি। আজ আপনি এখানে কেন এসেছেন?",
                "mr": "नमस्कार! मी तुमच्या आरोग्य समस्यांमध्ये मदत करण्यासाठी येथे आहे. आज तुम्हाला येथे काय आणले?",
                "gu": "નમસ્તે! હું તમારી સ્વાસ્થ્ય સમસ્યાઓમાં મદદ કરવા માટે અહીં છું. આજે તમને અહીં શું લાવ્યું?",
                "kn": "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಆರೋಗ್ಯ ಸಮಸ್ಯೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ಇಂದು ನಿಮ್ಮನ್ನು ಇಲ್ಲಿಗೆ ಏನು ತಂದಿತು?",
                "ml": "നമസ്കാരം! നിങ്ങളുടെ ആരോഗ്യ പ്രശ്നങ്ങളിൽ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. ഇന്ന് നിങ്ങളെ ഇവിടെ എത്തിച്ചത് എന്താണ്?",
                "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀਆਂ ਸਿਹਤ ਸਮੱਸਿਆਵਾਂ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ। ਅੱਜ ਤੁਹਾਨੂੰ ਇੱਥੇ ਕੀ ਲਿਆਇਆ?",
                "or": "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କ ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟାରେ ସାହାଯ୍ୟ କରିବାକୁ ଏଠାରେ ଅଛି। ଆଜି ଆପଣଙ୍କୁ ଏଠାକୁ କଣ ଆଣିଲା?",
            }
            greeting = fallback_greetings.get(language, fallback_greetings["en"])
            
            return {
                "session_id": session_id,
                "message": greeting,
                "language": language
            }
    
    def chat(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            session_id: Session identifier
            user_message: User's message
            
        Returns:
            AI response with extracted information
        """
        if session_id not in self.sessions:
            return {
                "error": "Session not found. Please start a new session.",
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        language = session.get("language", "en")
        
        # Language names for better prompting
        language_names = {
            "en": "English",
            "hi": "Hindi (हिंदी)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "bn": "Bengali (বাংলা)",
            "mr": "Marathi (मराठी)",
            "gu": "Gujarati (ગુજરાતી)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "ml": "Malayalam (മലയാളം)",
            "pa": "Punjabi (ਪੰਜਾਬੀ)",
            "or": "Odia (ଓଡ଼ିଆ)"
        }
        
        language_name = language_names.get(language, "English")
        
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build conversation context
        conversation_history = self._build_conversation_context(session)
        
        # Generate response
        try:
            prompt = f"""{self.system_prompt}

CRITICAL LANGUAGE INSTRUCTION - READ CAREFULLY:
- You MUST respond ONLY in {language_name}
- Do NOT use English or any other language in your response
- Write your ENTIRE response in {language_name} script
- The user is speaking in {language_name}, so you MUST reply in {language_name}
- Even if you understand English, respond in {language_name}
- This is MANDATORY - no exceptions

Conversation so far:
{conversation_history}

User: {user_message}

Task: Respond naturally in {language_name} and ask relevant follow-up questions. If you've gathered enough information (symptoms, duration, severity), suggest they proceed with the assessment. 

REMEMBER: Your ENTIRE response must be in {language_name} ONLY. Do not mix languages."""
            
            # Use generation config for better control
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 500,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            ai_message = response.text
            
            # Store AI response
            session["messages"].append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Extract information from conversation
            self._extract_information(session)
            
            logger.info(f"Chat response generated for session {session_id} in {language_name}")
            
            return {
                "session_id": session_id,
                "message": ai_message,
                "extracted_info": session["extracted_info"],
                "message_count": len(session["messages"])
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            # Fallback error messages in different languages
            fallback_errors = {
                "en": "I apologize, I'm having trouble processing that. Could you please rephrase?",
                "hi": "मुझे खेद है, मुझे इसे समझने में परेशानी हो रही है। क्या आप कृपया दोबारा बता सकते हैं?",
                "ta": "மன்னிக்கவும், அதை செயலாக்குவதில் எனக்கு சிக்கல் உள்ளது. தயவுசெய்து மீண்டும் சொல்ல முடியுமா?",
                "te": "క్షమించండి, దానిని ప్రాసెస్ చేయడంలో నాకు ఇబ్బంది ఉంది. దయచేసి మళ్లీ చెప్పగలరా?",
                "bn": "আমি দুঃখিত, আমি এটি প্রক্রিয়া করতে সমস্যা হচ্ছে। আপনি কি দয়া করে আবার বলতে পারেন?",
                "mr": "मला माफ करा, मला ते प्रक्रिया करण्यात अडचण येत आहे. कृपया पुन्हा सांगू शकाल का?",
                "gu": "માફ કરશો, મને તે પ્રક્રિયા કરવામાં મુશ્કેલી આવી રહી છે. કૃપા કરીને ફરીથી કહી શકશો?",
                "kn": "ಕ್ಷಮಿಸಿ, ಅದನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ನನಗೆ ತೊಂದರೆಯಾಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಹೇಳಬಹುದೇ?",
                "ml": "ക്ഷമിക്കണം, അത് പ്രോസസ്സ് ചെയ്യുന്നതിൽ എനിക്ക് പ്രശ്നമുണ്ട്. ദയവായി വീണ്ടും പറയാമോ?",
                "pa": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਇਸ ਨੂੰ ਪ੍ਰੋਸੈਸ ਕਰਨ ਵਿੱਚ ਮੁਸ਼ਕਲ ਆ ਰਹੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਦੱਸ ਸਕਦੇ ਹੋ?",
                "or": "କ୍ଷମା କରନ୍ତୁ, ମୋତେ ଏହାକୁ ପ୍ରକ୍ରିୟାକରଣରେ ଅସୁବିଧା ହେଉଛି। ଦୟାକରି ପୁଣି କହିପାରିବେ କି?",
            }
            error_message = fallback_errors.get(language, fallback_errors["en"])
            
            return {
                "session_id": session_id,
                "message": error_message,
                "error": str(e)
            }
    
    def _build_conversation_context(self, session: Dict[str, Any]) -> str:
        """Build conversation history string"""
        context = []
        for msg in session["messages"][-6:]:  # Last 6 messages for context
            role = "Assistant" if msg["role"] == "assistant" else "User"
            context.append(f"{role}: {msg['content']}")
        return "\n".join(context)
    
    def _extract_information(self, session: Dict[str, Any]):
        """
        Extract symptoms and patient info from conversation
        """
        try:
            # Build conversation text
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in session["messages"]
            ])
            
            # Ask Gemini to extract structured information
            extraction_prompt = f"""Analyze this health conversation and extract information in JSON format:

{conversation_text}

Extract:
1. Symptoms mentioned (with severity if mentioned: mild/moderate/severe)
2. Duration of symptoms (if mentioned)
3. Patient info: age, gender (if mentioned)
4. Whether enough information has been gathered for assessment

Return ONLY valid JSON:
{{
  "symptoms": [
    {{"name": "symptom_name", "severity": "moderate", "duration": "2 days"}}
  ],
  "patient_info": {{"age": 30, "gender": "male"}},
  "ready_for_assessment": true/false
}}

If information is not mentioned, omit those fields."""
            
            response = self.model.generate_content(extraction_prompt)
            
            # Parse JSON response
            json_text = response.text.strip()
            # Remove markdown code blocks if present
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif json_text.startswith("```"):
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            extracted = json.loads(json_text)
            
            # Update session with extracted info
            if "symptoms" in extracted:
                session["extracted_info"]["symptoms"] = extracted["symptoms"]
            if "patient_info" in extracted:
                session["extracted_info"]["patient_info"] = extracted["patient_info"]
            if "ready_for_assessment" in extracted:
                session["extracted_info"]["ready_for_assessment"] = extracted["ready_for_assessment"]
            
            logger.info(f"Extracted info: {session['extracted_info']}")
            
        except Exception as e:
            logger.warning(f"Could not extract information: {e}")
            # Don't fail the conversation if extraction fails
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str):
        """End and cleanup session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Ended session {session_id}")

# Global instance
gemini_service = GeminiConversationService()
