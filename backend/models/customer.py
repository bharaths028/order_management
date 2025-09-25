from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from dependencies.database import Base

flag_enum = ENUM('y', 'n', name='flag_enum', create_type=True)

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(100), nullable=False)
    company_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    landline = Column(String(20))
    address = Column(Text)
    department = Column(String(50))
    title = Column(String(50))
    tag = Column(String(50))
    flag = Column(flag_enum)
    contact_owner = Column(String(100))
