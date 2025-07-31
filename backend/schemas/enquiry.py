from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .customer import Customer
import uuid

class EnquiryProductBase(BaseModel):
    product_id: uuid.UUID = Field(..., description="Product ID", example="550e8400-e29b-41d4-a716-446655440000")
    quantity: float = Field(..., description="Quantity requested", example=100.00)
    chemical_name: Optional[str] = Field(None, description="Chemical name", example="Propan-2-one")
    price: Optional[float] = Field(None, description="Price per unit", example=50.00)
    cas_number: Optional[str] = Field(None, description="CAS number", example="67-64-1")
    cat_number: Optional[str] = Field(None, description="Catalog number", example="isp-a049010")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight", example=58.08)
    variant: Optional[str] = Field(None, description="Packaging form", example="25kg Drum")
    flag: Optional[str] = Field(None, description="Flag (y/n) for known/unknown product", example="y")
    attachment_ref: Optional[str] = Field(None, description="Attachment reference", example="s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity": 100.00,
                "chemical_name": "Propan-2-one",
                "price": 50.00,
                "cas_number": "67-64-1",
                "cat_number": "isp-a049010",
                "molecular_weight": 58.08,
                "variant": "25kg Drum",
                "flag": "y",
                "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
            }
        }

class EnquiryBase(BaseModel):
    customer_id: uuid.UUID = Field(..., description="Customer ID", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field("open", description="Enquiry status (open/processed/closed)", example="open")
    products: List[EnquiryProductBase] = Field([], description="List of products in the enquiry")

class EnquiryCreate(EnquiryBase):
    enquiry_date: str = Field(..., description="Enquiry date (dd-mm-yyyy)", example="05-07-2025")
    enquiry_time: str = Field(..., description="Enquiry time (HH:MM:SS)", example="01:11:00")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust-001",
                "enquiry_date": "05-07-2025",
                "enquiry_time": "01:11:00",
                "status": "open",
                "products": [
                    {
                        "product_id": "550e8400-e29b-41d4-a716-446655440000",
                        "quantity": 100.00,
                        "chemical_name": "Propan-2-one",
                        "price": 50.00,
                        "cas_number": "67-64-1",
                        "cat_number": "isp-a049010",
                        "molecular_weight": 58.08,
                        "variant": "25kg Drum",
                        "flag": "y",
                        "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                    }
                ]
            }
        }

class EnquiryUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Enquiry status (open/processed/closed)", example="processed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "processed"
            }
        }

class Enquiry(EnquiryBase):
    enquiry_id: uuid.UUID = Field(..., description="Unique enquiry ID", example="550e8400-e29b-41d4-a716-446655440000")
    enquiry_datetime: datetime = Field(..., description="Combined enquiry date and time")
    enquiry_date: Optional[str] = Field(None, description="Enquiry date (dd-mm-yyyy)", example="05-07-2025")
    enquiry_time: Optional[str] = Field(None, description="Enquiry time (HH:MM:SS)", example="01:11:00")

    @validator('enquiry_date', 'enquiry_time', pre=True, always=True)
    def compute_date_time(cls, v, values):
        if 'enquiry_datetime' in values and values['enquiry_datetime']:
            if v is None or v == "":
                if 'enquiry_date' in cls.__fields__ and not v:
                    return values['enquiry_datetime'].strftime('%d-%m-%Y')
                elif 'enquiry_time' in cls.__fields__ and not v:
                    return values['enquiry_datetime'].strftime('%H:%M:%S')
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                "enquiry_date": "05-07-2025",
                "enquiry_time": "01:11:00",
                "status": "open",
                "products": [
                    {
                        "product_id": "550e8400-e29b-41d4-a716-446655440000",
                        "quantity": 100.00,
                        "chemical_name": "Propan-2-one",
                        "price": 50.00,
                        "cas_number": "67-64-1",
                        "cat_number": "550e8400-e29b-41d4-a716-446655440000",
                        "molecular_weight": 58.08,
                        "variant": "25kg Drum",
                        "flag": "y",
                        "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                    }
                ]
            }
        }

class Attachment(BaseModel):
    file_name: str = Field(..., description="Attachment file name", example="formula.png")
    file_url: str = Field(..., description="Attachment URL", example="s3://ordermanagement-attachments/temp/formula.png")
    file_type: str = Field(..., description="Attachment file type", example="image/png")

    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "formula.png",
                "file_url": "s3://ordermanagement-attachments/temp/formula.png",
                "file_type": "image/png"
            }
        }

class ProductRequest(BaseModel):
    product_name: str = Field(..., description="Product name", example="Acetone")
    quantity: float = Field(..., description="Quantity requested", example=100.00)
    chemical_name: Optional[str] = Field(None, description="Chemical name", example="Propan-2-one")
    price: Optional[float] = Field(None, description="Price per unit", example=50.00)
    cas_number: Optional[str] = Field(None, description="CAS number", example="67-64-1")
    cat_number: Optional[str] = Field(None, description="Catalog number", example="isp-a049010")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight", example=58.08)
    variant: Optional[str] = Field(None, description="Packaging form", example="25kg Drum")

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Acetone",
                "quantity": 100.00,
                "chemical_name": "Propan-2-one",
                "price": 50.00,
                "cas_number": "67-64-1",
                "cat_number": "isp-a049010",
                "molecular_weight": 58.08,
                "variant": "25kg Drum"
            }
        }

class EmailRequest(BaseModel):
    customer_id: uuid.UUID = Field(..., description="Customer ID", example="550e8400-e29b-41d4-a716-446655440000")
    email_content: str = Field(..., description="Email content", example="Request for Acetone, 100kg")
    products: List[ProductRequest] = Field(..., description="List of products in the email")
    attachments: List[Attachment] = Field(..., description="List of attachments")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                "email_content": "Request for Acetone, 100kg",
                "products": [
                    {
                        "product_name": "Acetone",
                        "quantity": 100.00,
                        "chemical_name": "Propan-2-one",
                        "price": 50.00,
                        "cas_number": "67-64-1",
                        "cat_number": "isp-a049010",
                        "molecular_weight": 58.08,
                        "variant": "25kg Drum"
                    }
                ],
                "attachments": [
                    {
                        "file_name": "formula.png",
                        "file_url": "s3://ordermanagement-attachments/temp/formula.png",
                        "file_type": "image/png"
                    }
                ]
            }
        }

class BulkEnquiryRequest(BaseModel):
    emails: List[EmailRequest] = Field(..., description="List of email requests to process")

    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    {
                        "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                        "email_content": "Request for Acetone, 100kg",
                        "products": [
                            {
                                "product_name": "Acetone",
                                "quantity": 100.00,
                                "chemical_name": "Propan-2-one",
                                "price": 50.00,
                                "cas_number": "67-64-1",
                                "cat_number": "isp-a049010",
                                "molecular_weight": 58.08,
                                "variant": "25kg Drum"
                            }
                        ],
                        "attachments": [
                            {
                                "file_name": "formula.png",
                                "file_url": "s3://ordermanagement-attachments/temp/formula.png",
                                "file_type": "image/png"
                            }
                        ]
                    }
                ]
            }
        }

class EnquiryStatus(BaseModel):
    enquiry_id: uuid.UUID = Field(..., description="Enquiry ID", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Enquiry status (accepted/rejected)", example="accepted")
    message: Optional[str] = Field(None, description="Status message", example="Enquiry queued for parsing")

    class Config:
        json_schema_extra = {
            "example": {
                "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "accepted",
                "message": "Enquiry queued for parsing"
            }
        }

class BulkEnquiryResponse(BaseModel):
    batch_id: uuid.UUID = Field(..., description="Batch ID for the bulk request", example="550e8400-e29b-41d4-a716-446655440000")
    enquiries: List[EnquiryStatus] = Field(..., description="List of enquiry statuses")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "550e8400-e29b-41d4-a716-446655440000",
                "enquiries": [
                    {
                        "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "accepted",
                        "message": "Enquiry queued for parsing"
                    },
                    {
                        "enquiry_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "rejected",
                        "message": "Duplicate enquiry detected (550e8400-e29b-41d4-a716-446655440000)"
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
                    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                    "enquiry_date": "05-07-2025",
                    "enquiry_time": "01:11:00",
                    "status": "open",
                    "products": [
                        {
                            "product_id": "550e8400-e29b-41d4-a716-446655440000",
                            "quantity": 100.00,
                            "chemical_name": "Propan-2-one",
                            "price": 50.00,
                            "cas_number": "67-64-1",
                            "cat_number": "isp-a049010",
                            "molecular_weight": 58.08,
                            "variant": "25kg Drum",
                            "flag": "y",
                            "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
                        }
                    ]
                },
                "customer": {
                    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Acme Corp",
                    "email": "contact@acme.com",
                    "phone": "+1-555-123-4567",
                    "mobile": "+1-555-987-6543",
                    "landline": "+1-555-111-2222",
                    "address": "123 Main St, City, Country",
                    "organization": "Acme Corporation",
                    "department": "Procurement",
                    "title": "Purchasing Manager",
                    "tag": "VIP",
                    "flag": "y",
                    "contact_owner": "ISP Email"
                }
            }
        }
