from sqlalchemy import Column, String, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from dependencies.database import Base

tag_enum = ENUM('vendor', 'web', 'internal', name='tag_enum', create_type=True)
approval_status_enum = ENUM('pending', 'approved', 'rejected', name='approval_status_enum', create_type=True)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(100), nullable=False)
    cas_number = Column(String(20), unique=True)
    cat_number = Column(String(20), unique=True, nullable=False)
    chemical_name = Column(String(100))
    molecular_formula = Column(String(50))
    molecular_weight = Column(DECIMAL(10, 2))
    smiles = Column(Text)
    source = Column(String(100))
    description = Column(Text)
    tag = Column(tag_enum)
    approval_status = Column(approval_status_enum, nullable=False, default='pending')
    inventory_status = Column(String(50), default='custom_synthesis')
    image = Column(Text)
    hsn_code = Column(String(20))
    shipping_temperature = Column(String(50))
    ambient = Column(String(50))
    technical_data = Column(Text)
    country_of_origin = Column(String(50), default='india')
