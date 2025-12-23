# Order Management API

A production-ready FastAPI application with Apache Airflow orchestration for automated email parsing and enquiry management. This system integrates AWS Bedrock (Claude 3 Sonnet) for intelligent email extraction, PostgreSQL for data persistence, and Docker for containerized deployment.

## 🚀 Quick Start

### Local Development (Docker)
```bash
# Build and start all services
docker-compose up -d

# Access services
FastAPI:  http://localhost:8000
Airflow:  http://localhost:8080
Database: localhost:5432

# View logs
docker-compose logs -f fastapi-app
```

### Production Deployment
Choose your deployment method:
- **Docker Compose (Single Container)**: `docker-compose -f docker-compose.prod.yaml --profile prod up -d`
- **AWS ECS**: See [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)
- **AWS EC2**: See [PRODUCTION_QUICKSTART.md](./PRODUCTION_QUICKSTART.md)

For complete deployment guide, refer to **[PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)**.

## 📚 Documentation Guide

| Document | Purpose |
|----------|---------|
| **[PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)** | Comprehensive deployment guide (AWS, ECS, EC2, Swarm, monitoring) |
| **[PRODUCTION_QUICKSTART.md](./PRODUCTION_QUICKSTART.md)** | One-page quick start with one-command deployments |
| **[SETUP_SUMMARY.md](./SETUP_SUMMARY.md)** | Complete component overview and architecture |
| **[FILE_STRUCTURE.md](./FILE_STRUCTURE.md)** | Dev vs Production file structure comparison |
| **[CLEANUP_INSTRUCTIONS.md](./CLEANUP_INSTRUCTIONS.md)** | Remove dev-only files for production |
| **[PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)#architecture** | Architecture diagrams and process flow |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Container                       │
│                                                          │
│  ┌────────────────────┐        ┌──────────────────┐   │
│  │  FastAPI (Port 8000)│◄──────►│  PostgreSQL      │   │
│  │  (Uvicorn, 4 workers)       │  (Local/Aurora)  │   │
│  └────────────────────┘        └──────────────────┘   │
│           ▲                                             │
│           │                                             │
│  ┌────────┴──────────┐                                 │
│  │                   │                                 │
│  │  AIRFLOW          │                                 │
│  │  (Background)     │                                 │
│  │ ┌─────────────┐   │  ┌─────────────────────────┐   │
│  │ │ Scheduler   │   │  │ Email Parsing DAG       │   │
│  │ ├─────────────┤   │  ├─────────────────────────┤   │
│  │ │ Webserver   │◄──┤  │ 1. Fetch Gmail emails   │   │
│  │ │ (8080)      │   │  │ 2. Extract with Bedrock │   │
│  │ │             │   │  │ 3. Create enquiries     │   │
│  │ └─────────────┘   │  │ 4. Send acknowledgment  │   │
│  └────────────────────┘  └─────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
      AWS Bedrock    AWS Aurora      S3 Attachments
    (Claude 3 Sonnet) (Production)   (Optional)
```

## ✨ Features

- **🤖 AI-Powered Email Parsing**: Claude 3 Sonnet via AWS Bedrock extracts:
  - Customer information
  - Product details (chemicals, quantities)
  - Special requirements
  - Pricing information

- **📧 Automated Email Workflow**: 
  - Fetch emails from Gmail IMAP
  - Extract enquiry data with AI
  - Create enquiries automatically
  - Send acknowledgment emails

- **🗄️ Unified Database**:
  - Development: Local PostgreSQL in Docker
  - Production: AWS Aurora PostgreSQL
  - Single instance shared by FastAPI and Airflow

- **⚙️ Orchestration**:
  - Apache Airflow 2.10.2
  - Email parsing DAG with configurable schedule
  - Background processes (dev) or separate containers (prod)

- **🐳 Docker-Ready**:
  - Single production container (FastAPI + Airflow background processes)
  - Multi-service development environment
  - Docker Compose orchestration

- **☁️ Cloud-Native**:
  - AWS Bedrock integration
  - AWS Aurora PostgreSQL
  - AWS ECR/ECS deployment support
  - Environment-based configuration

## 📋 Prerequisites

### Development (Local)
- Docker & Docker Compose
- 4GB+ RAM available
- 2GB disk space

### Production (AWS)
- AWS Account with Bedrock API access
- AWS Aurora PostgreSQL instance
- AWS ECR repository (optional, for containerized deployment)
- IAM user with Bedrock, RDS, and ECR permissions

### Email Integration (Both)
- Gmail account (sender)
- Gmail account or email box (IMAP inbox to parse)
- Gmail App Password (2FA enabled)
- SMTP credentials

## 🚀 Installation & Setup

### Option 1: Local Docker Development (Fastest)

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd order_management/backend
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your Gmail and AWS credentials
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Verify services**
   ```bash
   # FastAPI health check
   curl http://localhost:8000/health
   
   # Airflow login (airflow/airflow by default)
   open http://localhost:8080
   ```

### Option 2: Production Deployment (AWS ECS)

See [PRODUCTION_QUICKSTART.md](./PRODUCTION_QUICKSTART.md) for one-command deployment.

Detailed instructions in [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md).

## 🔌 API Endpoints

### Core Endpoints
- **POST `/v1/enquiries/`** - Create enquiry
- **GET `/v1/enquiries/{enquiry_id}`** - Retrieve enquiry
- **GET `/v1/enquiries/`** - List enquiries (filters: status, skip, limit)
- **PUT `/v1/enquiries/{enquiry_id}`** - Update enquiry
- **POST `/v1/customers/`** - Create customer
- **GET `/health`** - Health check

### Example: Create Enquiry
```bash
curl -X POST http://localhost:8000/v1/enquiries/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-001",
    "enquiry_id": "isp02/25/0020",
    "enquiry_date": "05-07-2025",
    "enquiry_time": "01:11:00",
    "status": "open",
    "products": [{
      "product_id": "isp-a123",
      "chemical_name": "Propan-2-one",
      "quantity": 100,
      "cas_number": "67-64-1",
      "price": 50.0
    }]
  }'
```

## 🔧 Configuration

### Environment Variables

**Development** (`.env`):
```env
ENVIRONMENT=development
DATABASE_URL=postgresql://admin:admin123@postgres:5432/order_management
API_BASE_URL=http://fastapi:8000/v1
```

**Production** (`.env.prod`):
```env
ENVIRONMENT=production
AWS_DATABASE_URL=postgresql://user:pass@aurora-endpoint:5432/order_management
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_REGION=us-east-1
```

See `.env.prod` template for complete configuration options.

### Bedrock Configuration
Requires AWS credentials with Bedrock access:
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
```

Model: `anthropic.claude-3-sonnet-20240229-v1:0`

## 📊 Monitoring

### Local Development
```bash
# FastAPI logs
docker-compose logs -f fastapi-app

# Airflow logs
docker-compose logs -f airflow-scheduler

# Database health
docker-compose ps
```

### Production (AWS)
- CloudWatch Logs for container output
- CloudWatch Metrics for performance
- RDS monitoring for database health
- See [PRODUCTION_DEPLOYMENT.md#monitoring](./PRODUCTION_DEPLOYMENT.md) for detailed setup

## 🐛 Troubleshooting

### Common Issues

**"Database connection failed"**
- Check PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL in `.env`
- Check network: `docker network ls`

**"Bedrock API error"**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check region has Bedrock access
- Verify IAM permissions for bedrock:InvokeModel

**"Email parsing fails"**
- Check Gmail credentials in Airflow Variables
- Verify IMAP is enabled on Gmail account
- Check logs: `docker-compose logs email-parsing-dag`

For more troubleshooting, see [PRODUCTION_DEPLOYMENT.md#troubleshooting](./PRODUCTION_DEPLOYMENT.md).

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration management (environment-aware)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Development Docker image
├── Dockerfile.prod        # Production Docker image
├── docker-compose.yaml    # Development orchestration
├── docker-compose.prod.yaml # Production orchestration
├── start.sh              # Production startup script
│
├── api/v1/               # API routes
│   ├── enquiries.py
│   ├── customers.py
│   └── products.py
│
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
├── crud/                 # Database operations
├── scripts/              # Utility scripts
│   ├── email_parsing.py  # Bedrock integration for email extraction
│   └── email_parsing_manual.py
│
├── dags/                 # Airflow DAGs
│   └── email_parsing_dag.py
│
└── documentation/
    ├── PRODUCTION_DEPLOYMENT.md
    ├── PRODUCTION_QUICKSTART.md
    ├── SETUP_SUMMARY.md
    └── more...
```

## 🚢 Deployment Quick Reference

### Development → Production Checklist
- [ ] Update `.env` with production values
- [ ] Set AWS_DATABASE_URL to Aurora endpoint
- [ ] Configure AWS Bedrock region and credentials
- [ ] Update Gmail credentials in Airflow Variables
- [ ] Test locally: `docker-compose -f docker-compose.prod.yaml --profile dev up`
- [ ] Build production image: `docker build -f Dockerfile.prod -t order-management:prod .`
- [ ] Push to ECR or deploy to ECS/EC2

See [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) for detailed steps.

## 📝 License

Copyright 2025 Ideal Torque
```
