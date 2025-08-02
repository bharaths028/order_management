from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from models.enquiry import Enquiry
from models.enquiry_product import EnquiryProduct
from schemas.enquiry import EnquiryCreate, EmailRequest, EnquiryUpdate, Enquiry as EnquirySchema, EnquiryProductBase  # Added EnquiryProductBase
from schemas.product import ProductCreate
from crud.product import get_product, create_product
from utils.enquiry_id import generate_enquiry_id
from models.product import Product
from models.customer import Customer
import uuid

def get_enquiry(db: Session, enquiry_id: uuid.UUID):
    return db.query(Enquiry).options(joinedload(Enquiry.products), joinedload(Enquiry.customer)).filter(Enquiry.enquiry_id == enquiry_id).first()

def get_enquiries(db: Session, status: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Enquiry).options(joinedload(Enquiry.products), joinedload(Enquiry.customer))
    if status:
        query = query.filter(Enquiry.status == status)
    results = query.offset(skip).limit(limit).all()
    return [
        EnquirySchema(
            enquiry_id=enquiry.enquiry_id,
            customer_id=enquiry.customer_id,
            enquiry_datetime=enquiry.enquiry_datetime,
            status=enquiry.status,
            products=[
                EnquiryProductBase(
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
                for product in enquiry.products
            ],
            customer_name=enquiry.customer.customer_name if enquiry.customer else None,
            email=enquiry.customer.email if enquiry.customer else None
        )
        for enquiry in results
    ]

def create_enquiry(db: Session, enquiry: EnquiryCreate, enquiry_datetime: datetime):
    enquiry_id = uuid.uuid4()
    db_enquiry = Enquiry(
        enquiry_id=enquiry_id,
        customer_id=enquiry.customer_id,
        enquiry_datetime=enquiry_datetime,
        status=enquiry.status
    )
    db.add(db_enquiry)
    
    for product in enquiry.products:
        if product.product_id is None or not get_product(db, product.product_id):
            product_create = ProductCreate(
                product_id=uuid.uuid4(),
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

        db_product = EnquiryProduct(
            enquiry_id=enquiry_id,
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
    db_enquiry = db.query(Enquiry).options(joinedload(Enquiry.customer)).filter(Enquiry.enquiry_id == enquiry_id).first()
    if not db_enquiry:
        return None
    update_data = enquiry_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_enquiry, key, value)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry