from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from dependencies.database import get_db
from crud.customer import get_customer, get_customers, create_customer, update_customer
from schemas.customer import Customer, CustomerCreate, CustomerUpdate
from schemas.error import Error
import uuid

router = APIRouter()

@router.post(
    "/",
    response_model=Customer,
    status_code=201,
    summary="Create a new customer",
    description="Creates a new customer in the system.",
    operation_id="create_customer",
    responses={
        201: {"description": "Customer created", "model": Customer},
        400: {"description": "Invalid input", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        return create_customer(db, customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "err_invalid_input", "message": str(e)})

@router.get(
    "/",
    response_model=List[Customer],
    summary="List all customers",
    description="Retrieves a paginated list of all customers.",
    operation_id="list_customers",
    responses={
        200: {"description": "List of customers", "model": List[Customer]},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def list_customers(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    return get_customers(db, skip=skip, limit=limit)

@router.get(
    "/{customer_id}",
    response_model=Customer,
    summary="Get customer details",
    description="Retrieves details of a customer by ID.",
    operation_id="get_customer",
    responses={
        200: {"description": "Customer details", "model": Customer},
        404: {"description": "Customer not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def read_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    customer = get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Customer not found"})
    return customer

@router.patch(
    "/{customer_id}",
    response_model=Customer,
    summary="Update customer details",
    description="Updates details of an existing customer.",
    operation_id="update_customer",
    responses={
        200: {"description": "Customer updated", "model": Customer},
        400: {"description": "Invalid input", "model": Error},
        404: {"description": "Customer not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def update_customer_details(customer_id: uuid.UUID, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    customer = update_customer(db, customer_id, customer_update)
    if customer is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Customer not found"})
    return customer
