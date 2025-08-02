from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from models.enquiry import Enquiry
from models.enquiry_product import EnquiryProduct
from schemas.enquiry import EnquiryCreate, EmailRequest, EnquiryUpdate
from crud.product import get_product, create_product
from utils.enquiry_id import generate_enquiry_id
from models.product import Product
import uuid

def get_enquiry(db: Session, enquiry_id: uuid.UUID):
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
        # Check if product_id is None or product doesn't exist
        if not product.product_id or not get_product(db, product.product_id):
            # Create a new product if not present
            product_create = ProductCreate(
                product_id=uuid.uuid4(),  # Generate a UUID for product_id
                product_name=product.chemical_name or "Unnamed Product",
                cat_number=product.cat_number or f"ISP-A{uuid.uuid4().hex[:6]}",
                cas_number=product.cas_number,
                chemical_name=product.chemical_name,
                molecular_weight=product.molecular_weight,
                variant=product.variant,
                approval_status="pending"
            )
            new_product = create_product(db, product_create)
            product_id = new_product.product_id
        else:
            product_id = product.product_id

        # Create EnquiryProduct with the resolved product_id
        db_product = EnquiryProduct(
            enquiry_id=enquiry.enquiry_id,
            product_id=product_id,
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
    return db_enquiry

def create_enquiry_from_email(db: Session, email: EmailRequest, enquiry_id: uuid.UUID):
    enquiry_datetime = datetime.utcnow()
    db_enquiry = Enquiry(
        enquiry_id=enquiry_id,
        customer_id=email.customer_id,
        enquiry_datetime=enquiry_datetime,
        status="open"
    )
    db.add(db_enquiry)
    for product in email.products:
        # Create a temporary product_id for email-based enquiries
        product_create = ProductCreate(
            product_id=uuid.uuid4(),
            product_name=product.product_name,
            cat_number=product.cat_number or f"ISP-A{uuid.uuid4().hex[:6]}",
            cas_number=product.cas_number,
            chemical_name=product.chemical_name,
            molecular_weight=product.molecular_weight,
            variant=product.variant,
            approval_status="pending"
        )
        new_product = create_product(db, product_create)
        db_product = EnquiryProduct(
            enquiry_id=enquiry_id,
            product_id=new_product.product_id,
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

def update_enquiry(db: Session, enquiry_id: uuid.UUID, enquiry_update: EnquiryUpdate):
    db_enquiry = db.query(Enquiry).filter(Enquiry.enquiry_id == enquiry_id).first()
    if not db_enquiry:
        return None
    update_data = enquiry_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_enquiry, key, value)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry