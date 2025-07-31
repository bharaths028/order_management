from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid
from dependencies.database import Base

class ChangeLog(Base):
    __tablename__ = "change_log"
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String, nullable=False)
    record_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    details = Column(String)
