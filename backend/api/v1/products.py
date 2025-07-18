from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from dependencies.database import get_db
from crud.product import get_products, get_product, create_product
from schemas.product import Product, ProductCreate, ProductValidationRequest, ProductValidationResponse
from schemas.error import Error
from models.product import Product as ProductModel

router = APIRouter()

@router.post(
    "/",
    response_model=Product,
    status_code=201,
    summary="Create a new product",
    description="Creates a new product in the system.",
    operation_id="create_product",
    responses={
        201: {"description": "Product created", "model": Product},
        400: {"description": "Invalid input or duplicate CAS Number", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        return create_product(db, product)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "err_invalid_input", "message": str(e)})

@router.get(
    "/",
    response_model=List[Product],
    summary="List all products",
    description="Retrieves a paginated list of products, optionally filtered by approval status.",
    operation_id="list_products",
    responses={
        200: {"description": "List of products", "model": List[Product]},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def list_products(approval_status: Optional[str] = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    return get_products(db, approval_status=approval_status, skip=skip, limit=limit)

@router.get(
    "/{product_id}",
    response_model=Product,
    summary="Get product details",
    description="Retrieves details of a product by ID.",
    operation_id="get_product",
    responses={
        200: {"description": "Product details", "model": Product},
        404: {"description": "Product not found", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def read_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail={"code": "err_not_found", "message": "Product not found"})
    return product

@router.post(
    "/validate",
    response_model=List[ProductValidationResponse],
    summary="Validate enquiry products",
    description="Validates enquiry products against the Master Product Table.",
    operation_id="validate_products",
    responses={
        200: {"description": "Validation results", "model": List[ProductValidationResponse]},
        400: {"description": "Invalid input", "model": Error},
        429: {"description": "Rate limit exceeded", "model": Error}
    }
)
def validate_products(request: List[ProductValidationRequest], db: Session = Depends(get_db)):
    results = []
    for item in request:
        product = db.query(ProductModel).filter(
            (ProductModel.product_id == item.product_id) |
            (ProductModel.cas_number == item.cas_number) |
            (ProductModel.cat_number == item.cat_number)
        ).first()
        if product:
            results.append(ProductValidationResponse(
                enquiry_id=item.enquiry_id,
                product_id=item.product_id,
                flag="y",
                reason="Product found in Master Product Table"
            ))
        else:
            results.append(ProductValidationResponse(
                enquiry_id=item.enquiry_id,
                product_id=item.product_id,
                flag="n",
                reason="Product not found"
            ))
    return results
