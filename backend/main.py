from fastapi import FastAPI
from api.v1 import router as v1_router
from dependencies.database import engine, Base
import os

# FastAPI app with Swagger metadata
app = FastAPI(
    title="Centralized Automation & Order Management System API",
    description="API for managing customer enquiries, orders, quotations, inventory, and vendors with smart parsing, bulk processing, and parsing status monitoring.",
    version="1.0.1",
    openapi_tags=[
        {"name": "customers", "description": "Operations related to customer management"},
        {"name": "products", "description": "Operations related to product management"},
        {"name": "enquiries", "description": "Operations related to enquiry management and bulk processing"},
        {"name": "changelog", "description": "Operations related to retrieving change logs"},
        {"name": "health", "description": "System health check operations"}
    ],
    servers=[
        {"url": os.getenv("RENDER_EXTERNAL_URL", "https://order-management-api-knhi.onrender.com"), "description": "Production Server"},
        {"url": "http://localhost:8000", "description": "Production server"}
    ]
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API v1 router
app.include_router(v1_router, prefix="/v1")

@app.get(
    "/health",
    summary="Check system health",
    description="Check the health status of the system",
    tags=["health"],
    operation_id="check_health",
    responses={
        200: {"description": "System health status", "content": {"application/json": {"example": {"status": "healthy", "uptime": 99.99}}}},
        429: {"description": "Rate limit exceeded"}
    }
)
async def check_health():
    return {"status": "healthy", "uptime": 99.99}
