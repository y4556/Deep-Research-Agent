from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
import asyncio
from core.config import settings

class MultiModelCoordinator:
    """Orchestrates multiple AI models for different research tasks"""
    
    def __init__(self):
        self.models = {
            "openai_gpt4": ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY
            ),
            "claude_opus": ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.7,
                api_key=settings.ANTHROPIC_API_KEY
            ),
            "claude_sonnet": ChatAnthropic(
                model="claude-3-sonnet-20240229", 
                temperature=0.7,
                api_key=settings.ANTHROPIC_API_KEY
            ),
            "gemini_pro": ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.7,
                api_key=settings.GOOGLE_API_KEY
            )
        }
        
        # Model assignments for different tasks
        self.task_assignments = {
            "planning": "claude_opus",
            "query_generation": "openai_gpt4", 
            "fact_extraction": "claude_sonnet",
            "risk_assessment": "claude_opus",
            "reflection": "gemini_pro",
            "synthesis": "claude_opus"
        }
    
    async def generate_with_model(self, task_type: str, prompt: str, system_message: str = None) -> str:
        """Generate content using the appropriate model for the task"""
        model_name = self.task_assignments.get(task_type, "openai_gpt4")
        model = self.models[model_name]
        
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = await model.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            # Fallback to another model
            fallback_model = "openai_gpt4" if model_name != "openai_gpt4" else "gemini_pro"
            fallback = self.models[fallback_model]
            response = await fallback.ainvoke(messages)
            return response.content
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about model usage"""
        return {
            "available_models": list(self.models.keys()),
            "task_assignments": self.task_assignments,
            "total_models": len(self.models)
        }