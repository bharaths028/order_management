from sqlalchemy.orm import Session
from models.product import Product
from schemas.product import ProductCreate
import uuid

def get_product(db: Session, product_id: uuid):
    return db.query(Product).filter(Product.product_id == product_id).first()

def get_products(db: Session, approval_status: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Product)
    if approval_status:
        query = query.filter(Product.approval_status == approval_status)
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
