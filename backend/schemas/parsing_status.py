from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
import uuid

class ParsingStatus(BaseModel):
    enquiry_id: uuid.UUID = Field(..., description="Enquiry ID", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Parsing status (pending/processing/completed/failed)", example="processing")
    message: Optional[str] = Field(None, description="Parsing status message", example="Parsing image attachment")
    parsed_data: Optional[Dict] = Field(None, description="Parsed data", example={"products": [{"product_id": "550e8400-e29b-41d4-a716-446655440000", "quantity": 100.00}]})
    error_details: Optional[str] = Field(None, description="Error details", example="Failed to parse chemical formula image")
    timestamp: datetime = Field(..., description="Timestamp of the parsing status", example="2025-07-05T01:11:00Z")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "message": "Parsing image attachment",
                "parsed_data": {"products": [{"product_id": "550e8400-e29b-41d4-a716-446655440000", "quantity": 100.00}]},
                "error_details": None,
                "timestamp": "2025-07-05T01:11:00Z"
            }
        }
