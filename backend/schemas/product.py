from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    product_name: str = Field(..., description="Name of the product", example="Acetone")
    cat_number: str = Field(..., description="Catalog number (format ISP-{Alpha}{XXXXXX})", example="isp-a049010")
    cas_number: Optional[str] = Field(None, description="CAS number", example="67-64-1")
    chemical_name: Optional[str] = Field(None, description="Chemical name", example="Propan-2-one")
    molecular_formula: Optional[str] = Field(None, description="Molecular formula", example="C3H6O")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight", example=58.08)
    smiles: Optional[str] = Field(None, description="SMILES notation", example="CC(=O)C")
    source: Optional[str] = Field(None, description="Source of product data", example="PubChem")
    description: Optional[str] = Field(None, description="Product description", example="A volatile organic compound")
    tag: Optional[str] = Field(None, description="Product tag (vendor/web/internal)", example="internal")
    approval_status: str = Field("pending", description="Approval status (pending/approved/rejected)", example="approved")
    inventory_status: Optional[str] = Field("custom_synthesis", description="Inventory status", example="custom_synthesis")
    image: Optional[str] = Field(None, description="Image URL or reference", example="s3://images/acetone.png")
    hsn_code: Optional[str] = Field(None, description="HSN code", example="29141100")
    shipping_temperature: Optional[str] = Field(None, description="Shipping temperature", example="Room Temperature")
    ambient: Optional[str] = Field(None, description="Ambient conditions", example="Stable")
    technical_data: Optional[str] = Field(None, description="Technical data", example="95.5%")
    country_of_origin: Optional[str] = Field("india", description="Country of origin", example="india")

class ProductCreate(ProductBase):
    product_id: str = Field(..., description="Unique product identifier", example="isp-a123")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "isp-a123",
                "product_name": "Acetone",
                "cat_number": "isp-a049010",
                "cas_number": "67-64-1",
                "chemical_name": "Propan-2-one",
                "molecular_formula": "C3H6O",
                "molecular_weight": 58.08,
                "smiles": "CC(=O)C",
                "source": "PubChem",
                "description": "A volatile organic compound",
                "tag": "internal",
                "approval_status": "approved",
                "inventory_status": "custom_synthesis",
                "image": "s3://images/acetone.png",
                "hsn_code": "29141100",
                "shipping_temperature": "Room Temperature",
                "ambient": "Stable",
                "technical_data": "95.5%",
                "country_of_origin": "india"
            }
        }

class Product(ProductBase):
    product_id: str = Field(..., description="Unique product identifier", example="isp-a123")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_id": "isp-a123",
                "product_name": "Acetone",
                "cat_number": "isp-a049010",
                "cas_number": "67-64-1",
                "chemical_name": "Propan-2-one",
                "molecular_formula": "C3H6O",
                "molecular_weight": 58.08,
                "smiles": "CC(=O)C",
                "source": "PubChem",
                "description": "A volatile organic compound",
                "tag": "internal",
                "approval_status": "approved",
                "inventory_status": "custom_synthesis",
                "image": "s3://images/acetone.png",
                "hsn_code": "29141100",
                "shipping_temperature": "Room Temperature",
                "ambient": "Stable",
                "technical_data": "95.5%",
                "country_of_origin": "india"
            }
        }

class ProductValidationRequest(BaseModel):
    enquiry_id: str = Field(..., description="Enquiry ID", example="isp02/25/0020")
    product_id: str = Field(..., description="Product ID", example="isp-a123")
    cas_number: Optional[str] = Field(None, description="CAS number", example="67-64-1")
    cat_number: Optional[str] = Field(None, description="Catalog number", example="isp-a049010")

    class Config:
        json_schema_extra = {
            "example": {
                "enquiry_id": "isp02/25/0020",
                "product_id": "isp-a123",
                "cas_number": "67-64-1",
                "cat_number": "isp-a049010"
            }
        }

class ProductValidationResponse(BaseModel):
    enquiry_id: str = Field(..., description="Enquiry ID", example="isp02/25/0020")
    product_id: str = Field(..., description="Product ID", example="isp-a123")
    flag: str = Field(..., description="Flag (y/n) indicating if product is valid", example="y")
    reason: Optional[str] = Field(None, description="Reason for validation result", example="Product found in Master Product Table")

    class Config:
        json_schema_extra = {
            "example": {
                "enquiry_id": "isp02/25/0020",
                "product_id": "isp-a123",
                "flag": "y",
                "reason": "Product found in Master Product Table"
            }
        }
