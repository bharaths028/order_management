from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import uuid
from .customer import Customer

class EnquiryProductBase(BaseModel):
    product_id: Optional[uuid.UUID] = Field(None, description="Product ID (generated if not provided)", example="550e8400-e29b-41d4-a716-446655440001")
    quantity: float = Field(..., description="Quantity requested", example=100.00)
    chemical_name: Optional[str] = Field(None, description="Chemical name", example="Propan-2-one")
    cas_number: Optional[str] = Field(None, description="CAS number", example="67-64-1")
    cat_number: Optional[str] = Field(None, description="Catalog number", example="isp-a049010")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight", example=58.08)
    variant: Optional[str] = Field(None, description="Packaging form", example="25kg Drum")
    standards: Optional[str] = Field(None, description="Standards (USA/UK)", example="USA")
    flag: Optional[str] = Field(None, description="Flag (y/n) for known/unknown product", example="y")
    attachment_ref: Optional[str] = Field(None, description="Attachment reference", example="s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png")

    @validator('flag')
    def validate_and_normalize_flag(cls, v):
        if v is None:
            return None
        valid_flags = {"y", "n"}
        if v.lower() not in valid_flags:
            raise ValueError(f"Flag must be one of {valid_flags}")
        return v.lower()

    @validator('standards')
    def validate_standards(cls, v):
        if v is None:
            return None
        valid_standards = {"USA", "UK"}
        if v not in valid_standards:
            raise ValueError(f"Standards must be one of {valid_standards}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity": 100.00,
                "chemical_name": "Propan-2-one",
                "cas_number": "67-64-1",
                "cat_number": "isp-a049010",
                "molecular_weight": 58.08,
                "variant": "25kg Drum",
                "standards": "USA",
                "flag": "y",
                "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
            }
        }

class EnquiryBase(BaseModel):
    customer_id: uuid.UUID = Field(..., description="Customer ID", example="e000fa1f-c5d2-4250-af65-1ee6cfa041b7")
    status: str = Field("open", description="Enquiry status (open/processed/closed)", example="open")
    is_enquiry_active: bool = Field(True, description="Is the enquiry active?", example=True)
    enquiry_channel: str = Field("Email", description="Enquiry channel (Email/Portal)", example="Email")
    products: List[EnquiryProductBase] = Field(default_factory=list, description="List of products in the enquiry")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = {"open", "processed", "closed"}
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
            return v.lower()
        return v

    @validator('enquiry_channel')
    def validate_enquiry_channel(cls, v):
        if v is not None:
            valid_channels = {"Email", "Portal"}
            if v not in valid_channels:
                raise ValueError(f"Enquiry channel must be one of {valid_channels}")
            return v
        return v

class EnquiryCreate(EnquiryBase):
    enquiry_date: str = Field(..., description="Enquiry date (YYYY-MM-DD)", example="2025-09-25")
    enquiry_time: str = Field(..., description="Enquiry time (HH:MM)", example="01:53")

    @validator('enquiry_date')
    def validate_enquiry_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

    @validator('enquiry_time')
    def validate_enquiry_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "e000fa1f-c5d2-4250-af65-1ee6cfa041b7",
                "enquiry_date": "2025-09-25",
                "enquiry_time": "01:53",
                "status": "open",
                "is_enquiry_active": True,
                "enquiry_channel": "Email",
                "products": [
                    {
                        "quantity": 100,
                        "chemical_name": "Propan-2-one",
                        "cas_number": "67-64-1",
                        "cat_number": "isp-a049010",
                        "molecular_weight": 58.08,
                        "variant": "25kg Drum",
                        "standards": "USA",
                        "flag": "y",
                        "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                    }
                ]
            }
        }

class EnquiryUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Enquiry status (open/processed/closed)", example="processed")
    is_enquiry_active: Optional[bool] = Field(None, description="Is the enquiry active?", example=False)

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = {"open", "processed", "closed"}
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
            return v.lower()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "status": "processed",
                "is_enquiry_active": False
            }
        }

class Enquiry(EnquiryBase):
    enquiry_id: uuid.UUID = Field(..., description="Unique enquiry ID", example="550e8400-e29b-41d4-a716-446655440000")
    enquiry_name: str = Field(..., description="Unique enquiry name (ENQ-XXX)", example="ENQ-001")
    enquiry_datetime: datetime = Field(..., description="Combined enquiry date and time")
    enquiry_date: Optional[str] = Field(None, description="Enquiry date (YYYY-MM-DD)", example="2025-09-25")
    enquiry_time: Optional[str] = Field(None, description="Enquiry time (HH:MM)", example="01:53")
    customer_name: Optional[str] = Field(None, description="Name of the customer", example="Acme Corp")
    company_name: Optional[str] = Field(None, description="Customer's company name", example="Acme Industries")
    email: Optional[str] = Field(None, description="Customer email", example="contact@acme.com")

    @validator('enquiry_date', 'enquiry_time', pre=True, always=True)
    def compute_date_time(cls, v, values):
        if 'enquiry_datetime' in values and values['enquiry_datetime']:
            if v is None:
                if 'enquiry_date' in cls.__fields__:
                    return values['enquiry_datetime'].strftime('%Y-%m-%d')
                elif 'enquiry_time' in cls.__fields__:
                    return values['enquiry_datetime'].strftime('%H:%M')
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                "enquiry_name": "ENQ-001",
                "customer_id": "e000fa1f-c5d2-4250-af65-1ee6cfa041b7",
                "customer_name": "Acme Corp",
                "company_name": "Acme Industries",
                "enquiry_date": "2025-09-25",
                "enquiry_time": "01:53",
                "status": "open",
                "is_enquiry_active": True,
                "enquiry_channel": "Email",
                "products": [
                    {
                        "product_id": "550e8400-e29b-41d4-a716-446655440001",
                        "quantity": 100,
                        "chemical_name": "Propan-2-one",
                        "cas_number": "67-64-1",
                        "cat_number": "isp-a049010",
                        "molecular_weight": 58.08,
                        "variant": "25kg Drum",
                        "standards": "USA",
                        "flag": "y",
                        "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                    }
                ]
            }
        }

class EnquiryDashboardResponse(BaseModel):
    enquiry: Enquiry = Field(..., description="Enquiry details")
    customer: Customer = Field(..., description="Customer details")

    class Config:
        json_schema_extra = {
            "example": {
                "enquiry": {
                    "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                    "enquiry_name": "ENQ-001",
                    "customer_id": "e000fa1f-c5d2-4250-af65-1ee6cfa041b7",
                    "customer_name": "Acme Corp",
                    "company_name": "Acme Industries",
                    "enquiry_date": "2025-09-25",
                    "enquiry_time": "01:53",
                    "status": "open",
                    "is_enquiry_active": True,
                    "enquiry_channel": "Email",
                    "products": [
                        {
                            "product_id": "550e8400-e29b-41d4-a716-446655440001",
                            "quantity": 100.00,
                            "chemical_name": "Propan-2-one",
                            "cas_number": "67-64-1",
                            "cat_number": "isp-a049010",
                            "molecular_weight": 58.08,
                            "variant": "25kg Drum",
                            "standards": "USA",
                            "flag": "y",
                            "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                        }
                    ]
                },
                "customer": {
                    "customer_id": "e000fa1f-c5d2-4250-af65-1ee6cfa041b7",
                    "customer_name": "Acme Corp",
                    "company_name": "Acme Industries",
                    "email": "contact@acme.com",
                    "phone": "+1-555-123-4567",
                    "mobile": "+1-555-987-6543",
                    "landline": "+1-555-111-2222",
                    "address": "123 Main St, City, Country",
                    "department": "Procurement",
                    "title": "Purchasing Manager",
                    "tag": "VIP",
                    "flag": "y",
                    "contact_owner": "ISP Email"
                }
            }
        }
