from sqlalchemy import Column, Integer, String, TIMESTAMP
from dependencies.database import Base

class ChangeLog(Base):
    __tablename__ = "change_log"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String, nullable=False)
    record_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    details = Column(String)
