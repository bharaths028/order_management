from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import uuid
from dependencies.database import get_db
from crud.enquiry import get_enquiries, get_enquiry, create_enquiry, update_enquiry
from crud.customer import get_customer
from crud.parsing_status import get_parsing_status
from schemas.enquiry import Enquiry, EnquiryCreate, EnquiryUpdate, EnquiryDashboardResponse
from schemas.parsing_status import ParsingStatus
from schemas.error import Error
from models.enquiry import Enquiry as EnquiryModel
from models.customer import Customer as CustomerModel

router = APIRouter()

@router.post(
    "/",
    response_model=Enquiry,
    status_code=201,
    summary="Create a new enquiry",
    description="Creates a new enquiry from parsed UI or email data.",
    operation_id="create_enquiry",
    responses={
        201: {"description": "Enquiry created", "model": Enquiry},
        400: {"description": "Invalid input or parsing error", "model": Error},
        404: {"description": "Customer not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def create_new_enquiry(enquiry: EnquiryCreate, db: Session = Depends(get_db)):
    try:
        enquiry_datetime = datetime.strptime(f"{enquiry.enquiry_date} {enquiry.enquiry_time}:00", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail={"code": "err_invalid_input", "message": "Invalid date (YYYY-MM-DD) or time (HH:MM) format"})
    if not get_customer(db, enquiry.customer_id):
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Customer not found"})
    try:
        return create_enquiry(db, enquiry, enquiry_datetime)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "err_invalid_input", "message": str(e)})

@router.get(
    "/",
    response_model=List[Enquiry],
    summary="List all enquiries",
    description="Retrieves a paginated list of enquiries, optionally filtered by status.",
    operation_id="list_enquiries",
    responses={
        200: {"description": "List of enquiries", "model": List[Enquiry]},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def list_enquiries(status: Optional[str] = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    return get_enquiries(db, status, skip, limit)

@router.get(
    "/{enquiry_id}",
    response_model=Enquiry,
    summary="Get enquiry details",
    description="Retrieves details of an enquiry by ID.",
    operation_id="get_enquiry",
    responses={
        200: {"description": "Enquiry details", "model": Enquiry},
        404: {"description": "Enquiry not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def read_enquiry(enquiry_id: uuid.UUID, db: Session = Depends(get_db)):
    enquiry = get_enquiry(db, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Enquiry not found"})
    return enquiry

@router.patch(
    "/{enquiry_id}",
    response_model=Enquiry,
    summary="Update enquiry details",
    description="Updates details of an existing enquiry.",
    operation_id="update_enquiry",
    responses={
        200: {"description": "Enquiry updated", "model": Enquiry},
        400: {"description": "Invalid input", "model": Error},
        404: {"description": "Enquiry not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def update_enquiry_details(enquiry_id: uuid.UUID, enquiry_update: EnquiryUpdate, db: Session = Depends(get_db)):
    enquiry = update_enquiry(db, enquiry_id, enquiry_update)
    if enquiry is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Enquiry not found"})
    return enquiry

@router.get(
    "/{enquiry_id}/status",
    response_model=ParsingStatus,
    summary="Get parsing status",
    description="Retrieves the parsing status of an enquiry.",
    operation_id="get_parsing_status",
    responses={
        200: {"description": "Parsing status", "model": ParsingStatus},
        404: {"description": "Enquiry not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def read_parsing_status(enquiry_id: uuid.UUID, db: Session = Depends(get_db)):
    status = get_parsing_status(db, enquiry_id)
    if status is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Parsing status not found"})
    return status

@router.get(
    "/{enquiry_id}/dashboard",
    response_model=EnquiryDashboardResponse,
    summary="Get enquiry dashboard",
    description="Retrieves enquiry and customer details for dashboard display.",
    operation_id="get_enquiry_dashboard",
    responses={
        200: {"description": "Enquiry dashboard", "model": EnquiryDashboardResponse},
        404: {"description": "Enquiry or customer not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def read_enquiry_dashboard(enquiry_id: uuid.UUID, db: Session = Depends(get_db)):
    enquiry = db.query(EnquiryModel).options(joinedload(EnquiryModel.products)).filter(EnquiryModel.enquiry_id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Enquiry not found"})
    customer = db.query(CustomerModel).filter(CustomerModel.customer_id == enquiry.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Customer not found"})
    return EnquiryDashboardResponse(enquiry=enquiry, customer=customer)
