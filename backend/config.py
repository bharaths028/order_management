import os

# Database configuration based on environment
# Development: Use local Docker PostgreSQL
# Production: Use AWS Aurora PostgreSQL (pass via DATABASE_URL env variable)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Production: AWS Aurora PostgreSQL
    # Must be set via DATABASE_URL environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable must be set for production deployment")
else:
    # Development: Local Docker PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:admin123@postgres:5432/order_management"
    )

# Extract host for logging (safely)
def get_db_host():
    try:
        return DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else "unknown"
    except:
        return "unknown"

print(f"Environment: {ENVIRONMENT}")
print(f"Database Host: {get_db_host()}")
