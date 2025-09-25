from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from models.enquiry import Enquiry
from models.enquiry_product import EnquiryProduct
from schemas.enquiry import EnquiryCreate, EnquiryUpdate, Enquiry as EnquirySchema, EnquiryProductBase
from schemas.product import ProductCreate
from crud.product import get_product, create_product, update_product, get_product_by_identifiers
from models.product import Product
from models.customer import Customer
import uuid

def generate_enquiry_name(db: Session) -> str:
    """Generate a unique enquiry name in the format ENQ-XXX."""
    last_enquiry = db.query(Enquiry).order_by(Enquiry.enquiry_name.desc()).first()
    if last_enquiry and last_enquiry.enquiry_name.startswith("ENQ-"):
        try:
            last_number = int(last_enquiry.enquiry_name.split("-")[1])
            new_number = last_number + 1
        except (IndexError, ValueError):
            new_number = 1
    else:
        new_number = 1
    return f"ENQ-{new_number:03d}"

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
            enquiry_name=enquiry.enquiry_name,
            customer_id=enquiry.customer_id,
            enquiry_datetime=enquiry.enquiry_datetime,
            status=enquiry.status,
            is_enquiry_active=enquiry.is_enquiry_active,
            enquiry_channel=enquiry.enquiry_channel,
            products=[
                EnquiryProductBase(
                    product_id=product.product_id,
                    quantity=product.quantity,
                    chemical_name=product.chemical_name,
                    cas_number=product.cas_number,
                    cat_number=product.cat_number,
                    molecular_weight=product.molecular_weight,
                    variant=product.variant,
                    standards=product.standards,
                    flag=product.flag,
                    attachment_ref=product.attachment_ref
                )
                for product in enquiry.products
            ],
            customer_name=enquiry.customer.customer_name if enquiry.customer else None,
            email=enquiry.customer.email if enquiry.customer else None,
            company_name=enquiry.customer.company_name if enquiry.customer else None
        )
        for enquiry in results
    ]

def create_enquiry(db: Session, enquiry: EnquiryCreate, enquiry_datetime: datetime):
    enquiry_id = uuid.uuid4()
    enquiry_name = generate_enquiry_name(db)
    db_enquiry = Enquiry(
        enquiry_id=enquiry_id,
        enquiry_name=enquiry_name,
        customer_id=enquiry.customer_id,
        enquiry_datetime=enquiry_datetime,
        status=enquiry.status,
        is_enquiry_active=True,
        enquiry_channel=enquiry.enquiry_channel
    )
    db.add(db_enquiry)
    
    for product in enquiry.products:
        # Check if product exists by chemical_name, cas_number, or cat_number
        existing_product = get_product_by_identifiers(
            db,
            chemical_name=product.chemical_name,
            cas_number=product.cas_number,
            cat_number=product.cat_number
        )
        
        if existing_product:
            # Update existing product
            product_create = ProductCreate(
                product_name=product.chemical_name or existing_product.product_name or "Unnamed Product",
                cat_number=product.cat_number or existing_product.cat_number,
                cas_number=product.cas_number or existing_product.cas_number,
                chemical_name=product.chemical_name or existing_product.chemical_name,
                molecular_formula=existing_product.molecular_formula,
                molecular_weight=product.molecular_weight or existing_product.molecular_weight,
                smiles=existing_product.smiles,
                source=existing_product.source,
                description=existing_product.description,
                tag=existing_product.tag,
                approval_status=existing_product.approval_status,
                inventory_status=existing_product.inventory_status,
                image=existing_product.image,
                hsn_code=existing_product.hsn_code,
                shipping_temperature=existing_product.shipping_temperature,
                ambient=existing_product.ambient,
                technical_data=existing_product.technical_data,
                country_of_origin=existing_product.country_of_origin or "india",
                variant=product.variant or existing_product.variant,
                standards=product.standards or existing_product.standards
            )
            updated_product = update_product(db, existing_product.product_id, product_create)
            product_id = updated_product.product_id
        else:
            # Create new product
            product_create = ProductCreate(
                product_name=product.chemical_name or "Unnamed Product",
                cat_number=product.cat_number or f"ISP-A{uuid.uuid4().hex[:6]}",
                cas_number=product.cas_number,
                chemical_name=product.chemical_name,
                molecular_formula=None,
                molecular_weight=product.molecular_weight,
                smiles=None,
                source=None,
                description=None,
                tag=None,
                approval_status="pending",
                inventory_status="custom_synthesis",
                image=None,
                hsn_code=None,
                shipping_temperature=None,
                ambient=None,
                technical_data=None,
                country_of_origin="india",
                variant=product.variant,
                standards=product.standards or "USA"
            )
            new_product = create_product(db, product_create)
            product_id = new_product.product_id

        db_product = EnquiryProduct(
            enquiry_id=enquiry_id,
            product_id=product_id,
            quantity=product.quantity,
            chemical_name=product.chemical_name,
            cas_number=product.cas_number,
            cat_number=product.cat_number,
            molecular_weight=product.molecular_weight,
            variant=product.variant,
            standards=product.standards,
            flag=product.flag,
            attachment_ref=product.attachment_ref
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
