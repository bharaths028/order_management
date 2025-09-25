from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.product import Product
from schemas.product import ProductCreate
import uuid

def get_product(db: Session, product_id: uuid.UUID):
    return db.query(Product).filter(Product.product_id == product_id).first()

def get_products(db: Session, approval_status: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Product)
    if approval_status:
        query = query.filter(Product.approval_status == approval_status)
    return query.offset(skip).limit(limit).all()

def get_product_by_identifiers(db: Session, chemical_name: str = None, cas_number: str = None, cat_number: str = None):
    if not any([chemical_name, cas_number, cat_number]):
        return None
    query = db.query(Product)
    filters = []
    if chemical_name:
        filters.append(Product.chemical_name.ilike(chemical_name))
    if cas_number:
        filters.append(Product.cas_number.ilike(cas_number))
    if cat_number:
        filters.append(Product.cat_number.ilike(cat_number))
    query = query.filter(or_(*filters))
    return query.first()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: uuid.UUID, product_update: ProductCreate):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        return None
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product
