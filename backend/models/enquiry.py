from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from dependencies.database import Base
from sqlalchemy.orm import relationship

enquiry_status_enum = ENUM('open', 'processed', 'closed', name='enquiry_status_enum', create_type=True)

class Enquiry(Base):
    __tablename__ = "enquiries"
    enquiry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.customer_id'), nullable=False)
    enquiry_datetime = Column(TIMESTAMP, nullable=False)
    status = Column(enquiry_status_enum, nullable=False, default='open')
    change_log = Column(Text)
    customer = relationship("Customer")
    products = relationship("EnquiryProduct")
