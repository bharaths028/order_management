import os

# Database configuration based on environment
# Development: Use local Docker PostgreSQL
# Production: Use AWS Aurora PostgreSQL

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Production: AWS Aurora PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "AWS_DATABASE_URL",
            "postgresql://admin:password@order-management.c7jxyz.us-east-1.rds.amazonaws.com:5432/order_management"
        )
    )
else:
    # Development: Local Docker PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:admin123@postgres:5432/order_management"
    )

print(f"Environment: {ENVIRONMENT}")
print(f"Database URL (host): {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}")
