from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import ENUM
from dependencies.database import Base

parsing_status_enum = ENUM('pending', 'processing', 'completed', 'failed', name='parsing_status_enum', create_type=True)

class ParsingStatus(Base):
    __tablename__ = "parsing_status"
    parsing_status_id = Column(String(20), primary_key=True, unique=True)
    enquiry_id = Column(String(20), ForeignKey('enquiries.enquiry_id'))
    status = Column(parsing_status_enum, nullable=False)
    message = Column(Text)
    parsed_data = Column(JSON)
    error_details = Column(Text)
    timestamp = Column(TIMESTAMP, nullable=False)
