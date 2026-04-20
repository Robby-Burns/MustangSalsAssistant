import os
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import config

def get_llm_provider(model_type: str = "primary") -> BaseChatModel:
    """
    Fetches the standardized LLM provider.
    Reads from scale.yaml config to remain agnostic.
    # See .agents/workflows/08_AGNOSTIC_FACTORIES.md (The LLM Factory)
    """
    provider = config.llm.primary.provider.lower()
    model_name = config.llm.primary.model
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            from langchain_core.language_models import FakeListChatModel
            return FakeListChatModel(responses=["Mock OpenAI response"])
            
        # Lazy import so we don't blow up if dependency isn't installed
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=0, model=model_name)
        
    elif provider == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            from langchain_core.language_models import FakeListChatModel
            return FakeListChatModel(responses=["Mock Gemini response"])
            
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(temperature=0, model=model_name)
        
    # Default fail-safe
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
