from pydantic import BaseModel, Field, AnyHttpUrl
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class LeadContext(BaseModel):
    Lead_ID: str = Field(..., description="shopVOX identifier")
    Contact_Name: str
    Company: str
    Project_Type: str
    Pipeline_Stage: str
    Last_Activity_Date: datetime
    Open_Notes: str
    Address_Input: str
    Address_Geo_Lock: Optional[Dict[str, float]] = None

class ProjectRecipe(BaseModel):
    Recipe_ID: str
    Project_Type: str
    Part_List: List[Dict[str, Any]]
    Labor_Hours: int
    Zoning_Tags: List[str]
    Source_Bucket: Literal["Sandbox", "Legacy", "s3"]

class ComplianceRule(BaseModel):
    Jurisdiction: Literal["KMC", "RMC", "PMC"]
    Max_Sq_Ft: Optional[int] = None
    Height_Limit_Ft: int
    Setback_Ft: int
    Illumination_Notes: str
    Permit_Fee: Optional[float] = None
    Code_Citation: str
    Code_Link: AnyHttpUrl
    Verified_Geo: Dict[str, float]
    Jurisdiction_Name: str

class QuoteDraft(BaseModel):
    Quote_ID: str
    Lead_ID: str
    Project_Name: str
    Line_Items: List[Dict[str, Any]]
    Travel_SKU: str
    Travel_Fee_Amount: float
    Permit_Fees: float
    Gross_Margin_Pct: float
    Margin_Alert: bool
    Status: Literal["draft", "estimate_only", "approved_pending_submission"]
    Created_At: datetime
    Last_Updated: datetime

class CommDraft(BaseModel):
    Draft_ID: str
    Draft_Type: Literal["follow_up_email", "intro_email", "vector_request", "design_brief", "install_schedule"]
    Grounded_To: str
    Subject: str
    Body: str
    Recipient_Email: Optional[str] = None
    Generated_By: Literal["CommTemplateEngine"] = "CommTemplateEngine"
    Review_Required: bool = True
    Status: Literal["draft", "approved_not_sent", "sent_by_rep"]
