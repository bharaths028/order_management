from sqlalchemy.orm import Session
from models.parsing_status import ParsingStatus

def get_parsing_status(db: Session, enquiry_id: str):
    return db.query(ParsingStatus).filter(ParsingStatus.enquiry_id == enquiry_id).first()
