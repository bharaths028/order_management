# Order Management API

This is a FastAPI-based API application designed to manage customer enquiries and related products for an order management system. It provides endpoints for creating, retrieving, and updating enquiries, with data stored in a PostgreSQL database.

## Features
- Create and manage customer enquiries.
- Handle enquiry products with detailed attributes.
- Validate date and time inputs.
- Store data in a PostgreSQL database using SQLAlchemy.

## Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- Git (for cloning the repository)
- Virtual environment (recommended)

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone git@github.com:bharaths028/order_management.git
cd ordermanagement
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to isolate dependencies:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL
#### Install PostgreSQL
- Download and install PostgreSQL from [the official website](https://www.postgresql.org/download/) if not already installed.
- Follow the installation instructions for your operating system.

#### Create a Database
1. Open a terminal and connect to PostgreSQL using the `psql` command-line tool:
   ```bash
   psql -U postgres
   ```
   (Replace `postgres` with your PostgreSQL username if different, and enter your password when prompted.)

2. Create a new database named `ordermanagement`:
   ```sql
   CREATE DATABASE ordermanagement;
   ```

3. Exit the `psql` shell:
   ```sql
   \q
   ```

#### Configure Database Connection
- Open the `config.py` file in the project directory.
- Update the `DATABASE_URL` with your PostgreSQL credentials and database name. For example:
  ```python
  DATABASE_URL = "postgresql://username:password@localhost:5432/ordermanagement"
  ```
  - Replace `username` and `password` with your PostgreSQL username and password.
  - Ensure the port (`5432` by default) matches your PostgreSQL configuration.

### 5. Run the Application
Start the FastAPI app with Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. The application will automatically create the necessary database tables on startup.

## Using the API

### Create an Enquiry
Send a POST request to create a new enquiry:
```bash
curl -X 'POST' \
  'http://localhost:8000/v1/enquiries/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_id": "cust-001",
  "enquiry_date": "05-07-2025",
  "enquiry_id": "isp02/25/0020",
  "enquiry_time": "01:11:00",
  "products": [
    {
      "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png",
      "cas_number": "67-64-1",
      "cat_number": "isp-a049010",
      "chemical_name": "Propan-2-one",
      "flag": "y",
      "molecular_weight": 58.08,
      "price": 50,
      "product_id": "isp-a123",
      "quantity": 100,
      "variant": "25kg Drum"
    }
  ],
  "status": "open"
}'
```
**Expected Response (201 Created):**
```json
{
  "enquiry_id": "isp02/25/0020",
  "customer_id": "cust-001",
  "enquiry_datetime": "2025-07-05T01:11:00",
  "enquiry_date": "05-07-2025",
  "enquiry_time": "01:11:00",
  "status": "open",
  "products": [
    {
      "product_id": "isp-a123",
      "quantity": 100.0,
      "chemical_name": "Propan-2-one",
      "price": 50.0,
      "cas_number": "67-64-1",
      "cat_number": "isp-a049010",
      "molecular_weight": 58.08,
      "variant": "25kg Drum",
      "flag": "y",
      "attachment_ref": "s3://ordermanagement-attachments/enquiries/isp02-25-0020/isp-a123-formula.png"
    }
  ]
}
```

### Available Endpoints
- **POST `/v1/enquiries/`**: Create a new enquiry.
- **GET `/v1/enquiries/{enquiry_id}`**: Retrieve an enquiry by ID.
- **GET `/v1/enquiries/`**: List all enquiries (optional filters: `status`, `skip`, `limit`).
- **PUT `/v1/enquiries/{enquiry_id}`**: Update an existing enquiry.
- **POST `/v1/customers/`**: Create a new customer.

Refer to the code (e.g., `schemas/enquiry.py`) for detailed schema definitions.

## Error Handling
- **400 Bad Request**: Invalid input data or validation errors.
- **404 Not Found**: Resource not found.
- **500 Internal Server Error**: Unexpected server error (check logs).

## Troubleshooting
- If the API fails to start, ensure the PostgreSQL database is running and the `DATABASE_URL` is correct.
- Check the console logs for detailed error messages when issues arise.

## License
Copyright 2025 Ideal Torque
```
