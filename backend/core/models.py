from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
import asyncio
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class MultiModelCoordinator:
    """Orchestrates multiple AI models for different research tasks"""
    
    def __init__(self):
        
        self.models = {
            # ========== GROQ FREE MODELS (Fast & Reliable) ==========
            "groq_llama_70b": ChatGroq(
                model="llama-3.3-70b-versatile",  # Best Groq model
                temperature=0.7,
                api_key=settings.GROQ_API_KEY
            ),
            "groq_llama_8b": ChatGroq(
                model="llama-3.1-8b-instant",  # Fastest Groq model
                temperature=0.7,
                api_key=settings.GROQ_API_KEY
            ),
            "groq_mixtral": ChatGroq(
                model="mixtral-8x7b-32768",  # Good for complex tasks
                temperature=0.7,
                api_key=settings.GROQ_API_KEY
            ),
            
            # ========== OPENROUTER FREE MODELS (Powerful & Diverse) ==========
            "or_grok": ChatOpenAI(
                model="x-ai/grok-4.1-fast:free",  # X.AI's Grok - Fast & Smart
                temperature=0.7,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            ),
            "or_llama_70b": ChatOpenAI(
                model="meta-llama/llama-3.3-70b-instruct:free",  # Meta's best
                temperature=0.7,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            ),
            "or_mistral": ChatOpenAI(
                model="mistralai/mistral-small-3.2-24b-instruct:free",  # Mistral Small
                temperature=0.7,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            ),
            "or_gemma": ChatOpenAI(
                model="meta-llama/llama-3.1-8b-instruct:free",  # Llama 8B (reliable)
                temperature=0.7,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            ),
            "or_gpt_oss": ChatOpenAI(
                model="openai/gpt-oss-20b:free",  # GPT OSS
                temperature=0.7,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            ),
        }
        
        # 🎯 BEST MODEL FOR EACH TASK (Mix of Groq + OpenRouter)
        self.task_assignments = {
            "planning": "or_grok",              # Grok is excellent at planning 
            "query_generation": "groq_llama_8b", # Fast Groq for quick queries 
            "fact_extraction": "or_gemma",      # Gemma is good at extraction 
            "risk_assessment": "or_llama_70b",  # Llama 70B for critical analysis 
            "reflection": "or_mistral",         # Mistral is great at reflection 
            "synthesis": "or_grok"              # Grok for comprehensive synthesis
        }
    
    async def generate_with_model(self, task_type: str, prompt: str, system_message: str = None) -> str:
        """Generate content using the appropriate model for the task"""
        model_name = self.task_assignments.get(task_type, "or_grok")
        model = self.models[model_name]
        
        # 🔍 LOG EVERY LLM CALL
        logger.info("="*80)
        logger.info(f"🤖 LLM CALL - Task: {task_type.upper()}")
        logger.info(f"📦 Model: {model_name}")
        if system_message:
            logger.info(f"📋 System: {system_message[:100]}...")
        logger.info(f"💬 Prompt: {prompt[:200]}...")
        logger.info("="*80)
        
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = await model.ainvoke(messages)
            logger.info(f"✅ Response from {model_name}: {response.content[:200]}...")
            return response.content
        except Exception as e:
            logger.error(f"Error with {model_name}: {e}")
            
            # 🔄 SMART FALLBACK: If OpenRouter fails, try Groq. If Groq fails, try OpenRouter.
            fallback_chain = []
            if model_name.startswith("or_"):
                
                fallback_chain = ["groq_llama_70b", "groq_llama_8b", "groq_mixtral"]
            elif model_name.startswith("groq_"):
                
                fallback_chain = ["or_grok", "or_llama_70b", "or_mistral"]
            else:
                
                fallback_chain = ["or_grok", "groq_llama_70b"]
            
            
            for fallback_model in fallback_chain:
                try:
                    logger.warning(f"Falling back to {fallback_model}...")
                    fallback = self.models[fallback_model]
                    response = await fallback.ainvoke(messages)
                    logger.info(f"Fallback response from {fallback_model}: {response.content[:200]}...")
                    return response.content
                except Exception as fallback_error:
                    logger.error(f"Fallback model {fallback_model} also failed: {fallback_error}")
                    continue  
            
        
            raise Exception(f"All models failed including fallbacks. Original error: {e}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about model usage"""
        return {
            "available_models": list(self.models.keys()),
            "task_assignments": self.task_assignments,
            "total_models": len(self.models)
        }