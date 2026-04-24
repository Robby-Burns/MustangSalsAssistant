import logging
import os
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field, validator

load_dotenv()
logger = logging.getLogger(__name__)

class PlatformsConfig(BaseModel):
    teams_enabled: bool = Field(default=True)
    slack_enabled: bool = Field(default=False)

class GovernanceConfig(BaseModel):
    compliance_data_owner: str
    technical_contact_email: EmailStr

class ComplianceSourceConfig(BaseModel):
    excel_file_path: str

class BusinessRulesConfig(BaseModel):
    margin_floor: float = Field(default=0.35, ge=0.0, le=1.0)

class ContextManagementConfig(BaseModel):
    max_history_messages: int = Field(default=10)
    truncation_strategy: str = Field(default="middle")
    rag_top_k_results: int = Field(default=3)
    archive_threshold_lines: int = Field(default=500)
    archive_threshold_age_days: int = Field(default=14)

class OrchestrationConfig(BaseModel):
    engine: str = Field(default="langgraph")
    max_steps: int = Field(default=10)
    agent_workflow_enabled: bool = Field(default=True)
    human_in_the_loop_mandatory: bool = Field(default=True)

class LLMPrimaryConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.0)

class LLMEmbedderConfig(BaseModel):
    provider: str = Field(default="openai")

class LLMConfig(BaseModel):
    primary: LLMPrimaryConfig = Field(default_factory=LLMPrimaryConfig)
    embedder: LLMEmbedderConfig = Field(default_factory=LLMEmbedderConfig)

class DatabaseConfig(BaseModel):
    class VectorStoreConfig(BaseModel):
        provider: str = Field(default="chroma")
        collection_name: str = Field(default="mustang_recipes")
        chroma_persist_directory: str = Field(default="/app/chroma_db")

        def get_chroma_path(self) -> str:
            return self.chroma_persist_directory

    type: str = Field(default="vector")
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)

class AuditConfig(BaseModel):
    schedule_interval_months: int = Field(default=6)
    schedule_day: str = Field(default="1")
    schedule_time: str = Field(default="02:00")
    schedule_timezone: str = Field(default="UTC")
    notification_channel: str = Field(default="none")
    notification_link: Optional[str] = None
    auto_apply: bool = Field(default=False)
    cve_check_weekly: bool = Field(default=True)

class AppConfig(BaseModel):
    platforms: PlatformsConfig
    governance: GovernanceConfig
    compliance_source: ComplianceSourceConfig
    business_rules: BusinessRulesConfig
    context_management: ContextManagementConfig = Field(default_factory=ContextManagementConfig)
    orchestration: OrchestrationConfig = Field(default_factory=OrchestrationConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)

    @validator('compliance_source', pre=True, always=True)
    def set_demo_path(cls, v, values):
        app_mode = os.getenv("APP_MODE", "production").lower()
        if app_mode == 'demo':
            demo_path = "scripts/demo/demo_compliance_data.csv"
            logger.warning(f"APP_MODE is 'demo'. Overriding compliance data path to: {demo_path}")
            if isinstance(v, dict):
                v['excel_file_path'] = demo_path
            elif hasattr(v, 'excel_file_path'):
                v.excel_file_path = demo_path
        return v
    
    @classmethod
    def load(cls, yaml_path: str = "config/scale.yaml"):
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Configuration file not found at: {yaml_path}")
        with open(yaml_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        # Pydantic will automatically validate and load the nested models
        return cls(**yaml_config)

# Load configuration globally
try:
    config = AppConfig.load()
except FileNotFoundError as e:
    logger.error(e)
    # Create a default config or exit gracefully
    # For now, we'll exit if the config is essential
    raise SystemExit(f"CRITICAL: {e}") from e
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    raise SystemExit(f"CRITICAL: Could not load or validate config. {e}") from e
