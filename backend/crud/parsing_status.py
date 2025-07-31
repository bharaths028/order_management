from sqlalchemy.orm import Session
from models.parsing_status import ParsingStatus
import uuid

def get_parsing_status(db: Session, enquiry_id: uuid.UUID):
    return db.query(ParsingStatus).filter(ParsingStatus.enquiry_id == enquiry_id).first()
