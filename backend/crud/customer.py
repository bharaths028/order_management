from sqlalchemy.orm import Session
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate

def get_customer(db: Session, customer_id: str):
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: str, customer_update: CustomerUpdate):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        return None
    update_data = customer_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer
