from sqlalchemy.orm import Session
from models.enquiry_hash import EnquiryHash
from datetime import datetime

def get_enquiry_hash(db: Session, hash_value: str):
    return db.query(EnquiryHash).filter(EnquiryHash.hash == hash_value).first()

def store_enquiry_hash(db: Session, hash_value: str, enquiry_id: str):
    db_hash = EnquiryHash(
        hash=hash_value,
        enquiry_id=enquiry_id,
        created_at=datetime.utcnow()
    )
    db.add(db_hash)
    db.commit()
    db.refresh(db_hash)
    return db_hash
