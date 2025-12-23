from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from dependencies.database import Base

flag_enum = ENUM('y', 'n', name='flag_enum', create_type=True)
standards_enum = ENUM('USA', 'UK', name='standards_enum', create_type=True)

class EnquiryProduct(Base):
    __tablename__ = "enquiry_products"
    enquiry_product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enquiry_id = Column(UUID(as_uuid=True), ForeignKey('enquiries.enquiry_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    chemical_name = Column(Text)
    cas_number = Column(String(50))
    cat_number = Column(String(50))
    molecular_weight = Column(DECIMAL(10, 2))
    variant = Column(String(255))
    standards = Column(standards_enum)
    flag = Column(flag_enum)
    attachment_ref = Column(Text)
