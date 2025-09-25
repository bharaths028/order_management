from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from dependencies.database import Base
from sqlalchemy.orm import relationship

enquiry_status_enum = ENUM('open', 'processed', 'closed', name='enquiry_status_enum', create_type=True)
enquiry_channel_enum = ENUM('Email', 'Portal', name='enquiry_channel_enum', create_type=True)

class Enquiry(Base):
    __tablename__ = "enquiries"
    enquiry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enquiry_name = Column(String(10), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.customer_id'), nullable=False)
    enquiry_datetime = Column(TIMESTAMP, nullable=False)
    status = Column(enquiry_status_enum, nullable=False, default='open')
    is_enquiry_active = Column(Boolean, nullable=False, default=True)
    enquiry_channel = Column(enquiry_channel_enum, nullable=False, default='Email')
    change_log = Column(Text)
    customer = relationship("Customer")
    products = relationship("EnquiryProduct")
