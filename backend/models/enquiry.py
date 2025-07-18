from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM
from dependencies.database import Base
from sqlalchemy.orm import relationship

enquiry_status_enum = ENUM('open', 'processed', 'closed', name='enquiry_status_enum', create_type=True)

class Enquiry(Base):
    __tablename__ = "enquiries"
    enquiry_id = Column(String(20), primary_key=True, unique=True)
    customer_id = Column(String, ForeignKey('customers.customer_id'), nullable=False)
    enquiry_datetime = Column(TIMESTAMP, nullable=False)
    status = Column(enquiry_status_enum, nullable=False, default='open')
    change_log = Column(Text)
    customer = relationship("Customer")
    products = relationship("EnquiryProduct")
