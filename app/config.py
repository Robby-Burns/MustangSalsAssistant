from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
import yaml
import os

class ContextManagementConfig(BaseModel):
    max_history_messages: int
    truncation_strategy: str
    rag_top_k_results: int
    archive_threshold_lines: int = 500
    archive_threshold_age_days: int = 14

class OrchestrationConfig(BaseModel):
    engine: str
    max_steps: int

class PrimaryLLMConfig(BaseModel):
    provider: str
    model: str
    
class EmbedderConfig(BaseModel):
    provider: str

class LLMConfig(BaseModel):
    primary: PrimaryLLMConfig
    embedder: EmbedderConfig

class VectorStoreConfig(BaseModel):
    provider: str = Field(default="neon", description="The vector store provider: 'neon', 'chroma', or 's3'")
    chroma_persist_directory: str = Field(default="/app/chroma_db", description="Path for chroma DB local storage")
    collection_name: str = Field(default="project_recipes", description="Collection name for vector store")
    
    def get_chroma_path(self) -> str:
        """Returns the configured path if it exists as an absolute path (Docker), otherwise falls back to a relative path for local development."""
        if os.path.exists(self.chroma_persist_directory) or self.chroma_persist_directory.startswith("/app"):
            # Inside docker, or it exists.
            if self.chroma_persist_directory.startswith("/app") and not os.path.exists("/app"):
                 # We are outside of docker, fallback
                 return os.path.abspath("./chroma_db")
            return self.chroma_persist_directory
        return os.path.abspath("./chroma_db")


class DatabaseConfig(BaseModel):
    type: str
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)

class AuditConfig(BaseModel):
    schedule_interval_months: int
    schedule_day: str
    schedule_time: str
    schedule_timezone: str
    notification_channel: str
    notification_link: str
    auto_apply: bool  # Must always be False
    cve_check_weekly: bool

class AppConfig(BaseModel):
    context_management: ContextManagementConfig
    orchestration: OrchestrationConfig
    llm: LLMConfig
    database: DatabaseConfig
    audit: AuditConfig
    
    @classmethod
    def load(cls, yaml_path: str = "config/scale.yaml"):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {yaml_path}: {e}")
        
        config = cls(**config_data)
        
        # Hard safety check: auto_apply must never be True
        if config.audit.auto_apply:
            raise ValueError(
                "FATAL: audit.auto_apply is True. "
                "This is forbidden. Human sign-off is mandatory."
            )
        
        return config

# Crash immediately if config is broken
config = AppConfig.load()
