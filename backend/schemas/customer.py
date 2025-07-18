from pydantic import BaseModel, Field
from typing import Optional

class CustomerBase(BaseModel):
    name: str = Field(..., description="Customer's full name or organization name", example="Acme Corp")
    email: str = Field(..., description="Customer's email address", example="contact@acme.com")
    phone: Optional[str] = Field(None, description="Customer's phone number", example="+1-555-123-4567")
    mobile: Optional[str] = Field(None, description="Customer's mobile number", example="+1-555-987-6543")
    landline: Optional[str] = Field(None, description="Customer's landline number", example="+1-555-111-2222")
    address: Optional[str] = Field(None, description="Customer's address", example="123 Main St, City, Country")
    organization: Optional[str] = Field(None, description="Customer's organization", example="Acme Corporation")
    department: Optional[str] = Field(None, description="Customer's department", example="Procurement")
    title: Optional[str] = Field(None, description="Customer's title", example="Purchasing Manager")
    tag: Optional[str] = Field(None, description="Customer tag", example="VIP")
    flag: Optional[str] = Field(None, description="Flag (y/n) for known/unknown customer", example="y")
    contact_owner: Optional[str] = Field(None, description="Source of enquiry", example="ISP Email")

class CustomerCreate(CustomerBase):
    customer_id: str = Field(..., description="Unique customer identifier", example="cust-001")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust-001",
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

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Customer's full name or organization name", example="Acme Corp")
    email: Optional[str] = Field(None, description="Customer's email address", example="contact@acme.com")
    phone: Optional[str] = Field(None, description="Customer's phone number", example="+1-555-123-4567")
    mobile: Optional[str] = Field(None, description="Customer's mobile number", example="+1-555-987-6543")
    landline: Optional[str] = Field(None, description="Customer's landline number", example="+1-555-111-2222")
    address: Optional[str] = Field(None, description="Customer's address", example="123 Main St, City, Country")
    organization: Optional[str] = Field(None, description="Customer's organization", example="Acme Corporation")
    department: Optional[str] = Field(None, description="Customer's department", example="Procurement")
    title: Optional[str] = Field(None, description="Customer's title", example="Purchasing Manager")
    tag: Optional[str] = Field(None, description="Customer tag", example="VIP")
    flag: Optional[str] = Field(None, description="Flag (y/n) for known/unknown customer", example="y")
    contact_owner: Optional[str] = Field(None, description="Source of enquiry", example="ISP Email")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corp Updated",
                "email": "newcontact@acme.com"
            }
        }

class Customer(CustomerBase):
    customer_id: str = Field(..., description="Unique customer identifier", example="cust-001")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "customer_id": "cust-001",
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
