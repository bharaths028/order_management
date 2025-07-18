from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class ParsingStatus(BaseModel):
    enquiry_id: str = Field(..., description="Enquiry ID", example="isp02/25/0020")
    status: str = Field(..., description="Parsing status (pending/processing/completed/failed)", example="processing")
    message: Optional[str] = Field(None, description="Parsing status message", example="Parsing image attachment")
    parsed_data: Optional[Dict] = Field(None, description="Parsed data", example={"products": [{"product_id": "isp-a123", "quantity": 100.00}]})
    error_details: Optional[str] = Field(None, description="Error details", example="Failed to parse chemical formula image")
    timestamp: datetime = Field(..., description="Timestamp of the parsing status", example="2025-07-05T01:11:00Z")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "enquiry_id": "isp02/25/0020",
                "status": "processing",
                "message": "Parsing image attachment",
                "parsed_data": {"products": [{"product_id": "isp-a123", "quantity": 100.00}]},
                "error_details": None,
                "timestamp": "2025-07-05T01:11:00Z"
            }
        }
