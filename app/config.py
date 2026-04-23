import logging
from pydantic import BaseModel, Field, EmailStr, validator
import yaml
import os
from dotenv import load_dotenv

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
    # ... (rest of the config models remain the same)
    pass

class OrchestrationConfig(BaseModel):
    # ...
    pass

class LLMConfig(BaseModel):
    # ...
    pass

class DatabaseConfig(BaseModel):
    # ...
    pass

class AuditConfig(BaseModel):
    # ...
    pass

class AppConfig(BaseModel):
    platforms: PlatformsConfig
    governance: GovernanceConfig
    compliance_source: ComplianceSourceConfig
    business_rules: BusinessRulesConfig
    # ... (rest of the AppConfig fields)

    @validator('compliance_source', pre=True, always=True)
    def set_demo_path(cls, v, values):
        app_mode = os.getenv("APP_MODE", "production").lower()
        if app_mode == 'demo':
            demo_path = "scripts/demo/demo_compliance_data.xlsx"
            logger.warning(f"APP_MODE is 'demo'. Overriding compliance data path to: {demo_path}")
            # This assumes the input `v` is a dictionary that can be modified.
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
