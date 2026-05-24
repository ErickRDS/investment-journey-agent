"""LLM configuration for the investment journey agent."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def get_llm(temperature: float = 0.7, model: Optional[str] = None) -> ChatOpenAI:
    """
    Get configured ChatOpenAI instance.
    
    Args:
        temperature: Temperature for the LLM (0.0 to 1.0)
        model: Model name to use (defaults to env var OPENAI_MODEL)
        
    Returns:
        Configured ChatOpenAI instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY não encontrada. "
            "Por favor, configure a variável de ambiente no arquivo .env"
        )
    
    model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    logger.info(f"Inicializando LLM: {model_name} com temperature={temperature}")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


def check_llm_available() -> bool:
    """
    Check if LLM is available (API key is set).
    
    Returns:
        True if API key is configured, False otherwise
    """
    return bool(os.getenv("OPENAI_API_KEY"))
