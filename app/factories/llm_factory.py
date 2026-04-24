import os

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import config

def get_llm_provider(model_type: str = "primary") -> BaseChatModel:
    """
    Fetches the standardized LLM provider based on the configuration in scale.yaml.
    """
    llm_config = getattr(config.llm, model_type)
    provider = llm_config.provider.lower()
    model_name = llm_config.model

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            from langchain_core.language_models import FakeListChatModel
            return FakeListChatModel(responses=["Mock OpenAI response"])
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=llm_config.temperature, model=model_name)
        
    elif provider in {"gemini", "google"}:
        if not os.getenv("GOOGLE_API_KEY"):
            from langchain_core.language_models import FakeListChatModel
            return FakeListChatModel(responses=["Mock Gemini response"])
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(temperature=llm_config.temperature, model=model_name)

    elif provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            from langchain_core.language_models import FakeListChatModel
            return FakeListChatModel(responses=["Mock Anthropic response"])
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(temperature=llm_config.temperature, model_name=model_name)
        
    raise ValueError(f"Unsupported LLM provider specified in config: '{provider}'")
