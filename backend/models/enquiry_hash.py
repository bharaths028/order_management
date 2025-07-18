from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from dependencies.database import Base

class EnquiryHash(Base):
    __tablename__ = "enquiry_hash"
    enquiry_hash_id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(64))
    enquiry_id = Column(String(20), ForeignKey('enquiries.enquiry_id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
