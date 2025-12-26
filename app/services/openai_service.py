from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.prompts import get_system_prompt, build_personalized_prompt


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_content(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        if model is None:
            model = settings.DEFAULT_MODEL
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model_used": model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def generate_with_context(
        self,
        user_message: str,
        content_type: str,
        user_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: str = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate content with user context and history"""
        
        # Build system prompt
        if user_context:
            system_prompt = build_personalized_prompt(content_type, user_context)
        else:
            system_prompt = get_system_prompt(content_type)
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return await self.generate_content(
            messages=messages,
            model=model,
            temperature=temperature
        )
    
    async def generate_streaming(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7
    ):
        """Generate content with streaming"""
        if model is None:
            model = settings.DEFAULT_MODEL
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate text embedding"""
        try:
            response = await self.client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding generation error: {str(e)}")
    
    async def extract_context(
        self,
        user_message: str,
        assistant_message: str
    ) -> Dict[str, Any]:
        """Extract learnable context from conversation"""
        
        extraction_prompt = f"""
Analyze this conversation and extract key user preferences or context.
Return ONLY a JSON object with these keys (if applicable):
- writing_style: (casual, professional, technical, etc.)
- tone_preference: (friendly, formal, conversational, etc.)
- industry: (tech, finance, healthcare, etc.)
- target_audience: (developers, marketers, students, etc.)
- specific_preferences: (any other notable preferences)

User: {user_message}
Assistant: {assistant_message}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a context extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            import json
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, return empty dict
                return {}
        except Exception as e:
            print(f"Context extraction error: {str(e)}")
            return {}
    
    async def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        max_length: int = 200
    ) -> str:
        """Generate conversation summary"""
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        
        summary_prompt = f"""
Summarize this conversation in {max_length} words or less. 
Focus on key topics, decisions, and outputs generated.

{conversation_text}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a summarization expert."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Summary generation failed: {str(e)}"


openai_service = OpenAIService()