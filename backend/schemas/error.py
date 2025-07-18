from pydantic import BaseModel, Field
from typing import Optional, Dict

class Error(BaseModel):
    code: str = Field(..., description="Error code", example="err_invalid_input")
    message: str = Field(..., description="Error message", example="Invalid input data")
    details: Optional[Dict] = Field(None, description="Additional error details", example={"field": "email"})

    class Config:
        json_schema_extra = {
            "example": {
                "code": "err_invalid_input",
                "message": "Invalid input data",
                "details": {"field": "email"}
            }
        }
