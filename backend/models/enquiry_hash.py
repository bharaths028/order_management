from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from dependencies.database import Base

class EnquiryHash(Base):
    __tablename__ = "enquiry_hash"
    enquiry_hash_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash = Column(String(64))
    enquiry_id = Column(UUID(as_uuid=True), ForeignKey('enquiries.enquiry_id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
