from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChangeLog(BaseModel):
    log_id: int = Field(..., description="Unique log ID", example=1)
    table_name: str = Field(..., description="Table name", example="enquiries")
    record_id: str = Field(..., description="Record ID", example="isp02/25/0020")
    action: str = Field(..., description="Action performed (view/edit/create/delete/flag/system)", example="create")
    user_id: str = Field(..., description="User ID performing the action", example="user123")
    timestamp: datetime = Field(..., description="Timestamp of the action", example="2025-07-05T01:11:00Z")
    details: Optional[str] = Field(None, description="Details of the action", example="Created new enquiry")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "log_id": 1,
                "table_name": "enquiries",
                "record_id": "isp02/25/0020",
                "action": "create",
                "user_id": "user123",
                "timestamp": "2025-07-05T01:11:00Z",
                "details": "Created new enquiry"
            }
        }
