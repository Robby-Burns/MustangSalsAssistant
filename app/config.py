from pydantic import BaseModel, Field, EmailStr
import yaml
import os

class PlatformsConfig(BaseModel):
    teams_enabled: bool = Field(default=True)
    slack_enabled: bool = Field(default=False)

class GovernanceConfig(BaseModel):
    compliance_data_owner: str
    technical_contact_email: EmailStr

class ComplianceSourceConfig(BaseModel):
    excel_file_path: str

class ContextManagementConfig(BaseModel):
    max_history_messages: int
    truncation_strategy: str
    rag_top_k_results: int
    archive_threshold_lines: int = 500
    archive_threshold_age_days: int = 14

class OrchestrationConfig(BaseModel):
    engine: str
    max_steps: int
    agent_workflow_enabled: bool = Field(default=False)

class PrimaryLLMConfig(BaseModel):
    provider: str
    model: str
    
class EmbedderConfig(BaseModel):
    provider: str

class LLMConfig(BaseModel):
    primary: PrimaryLLMConfig
    embedder: EmbedderConfig

class VectorStoreConfig(BaseModel):
    provider: str = Field(default="chroma")
    collection_name: str = Field(default="project_recipes")
    chroma_persist_directory: str = Field(default="/app/chroma_db")
    
    def get_chroma_path(self) -> str:
        if os.path.exists(self.chroma_persist_directory) or self.chroma_persist_directory.startswith("/app"):
            if self.chroma_persist_directory.startswith("/app") and not os.path.exists("/app"):
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
    auto_apply: bool
    cve_check_weekly: bool

class AppConfig(BaseModel):
    platforms: PlatformsConfig
    governance: GovernanceConfig
    compliance_source: ComplianceSourceConfig
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
        
        if config.audit.auto_apply:
            raise ValueError("FATAL: audit.auto_apply is True. Human sign-off is mandatory.")
        
        if not config.platforms.teams_enabled and not config.platforms.slack_enabled:
            raise ValueError("FATAL: No bot platforms enabled in config/scale.yaml.")

        return config

config = AppConfig.load()
