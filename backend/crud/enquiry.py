from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from models.enquiry import Enquiry
from models.enquiry_product import EnquiryProduct
from schemas.enquiry import EnquiryCreate, EmailRequest, EnquiryUpdate
from utils.enquiry_id import generate_enquiry_id

def get_enquiry(db: Session, enquiry_id: str):
    return db.query(Enquiry).options(joinedload(Enquiry.products)).filter(Enquiry.enquiry_id == enquiry_id).first()

def get_enquiries(db: Session, status: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Enquiry).options(joinedload(Enquiry.products))
    if status:
        query = query.filter(Enquiry.status == status)
    return query.offset(skip).limit(limit).all()

def create_enquiry(db: Session, enquiry: EnquiryCreate, enquiry_datetime: datetime):
    db_enquiry = Enquiry(
        enquiry_id=enquiry.enquiry_id,
        customer_id=enquiry.customer_id,
        enquiry_datetime=enquiry_datetime,
        status=enquiry.status
    )
    db.add(db_enquiry)
    for product in enquiry.products:
        db_product = EnquiryProduct(
            enquiry_id=enquiry.enquiry_id,
            product_id=product.product_id,
            quantity=product.quantity,
            chemical_name=product.chemical_name,
            price=product.price,
            cas_number=product.cas_number,
            cat_number=product.cat_number,
            molecular_weight=product.molecular_weight,
            variant=product.variant,
            flag=product.flag,
            attachment_ref=product.attachment_ref
        )
        db.add(db_product)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry  # Return the SQLAlchemy object

def create_enquiry_from_email(db: Session, email: EmailRequest, enquiry_id: str):
    enquiry_datetime = datetime.utcnow()
    db_enquiry = Enquiry(
        enquiry_id=enquiry_id,
        customer_id=email.customer_id,
        enquiry_datetime=enquiry_datetime,
        status="open"
    )
    db.add(db_enquiry)
    for product in email.products:
        db_product = EnquiryProduct(
            enquiry_id=enquiry_id,
            product_id=f"isp-temp-{hash(product.product_name)}",
            quantity=product.quantity,
            chemical_name=product.chemical_name,
            price=product.price,
            cas_number=product.cas_number,
            cat_number=product.cat_number,
            molecular_weight=product.molecular_weight,
            variant=product.variant
        )
        db.add(db_product)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry

def update_enquiry(db: Session, enquiry_id: str, enquiry_update: EnquiryUpdate):
    db_enquiry = db.query(Enquiry).filter(Enquiry.enquiry_id == enquiry_id).first()
    if not db_enquiry:
        return None
    update_data = enquiry_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_enquiry, key, value)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry