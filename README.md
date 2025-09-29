# Savannah Informatics - Backend Engineer Assessment
[![CI](https://github.com/stephenOwino/savannah-backend-engineer-test/workflows/Django%20CI/badge.svg)](https://github.com/stephenOwino/savannah-backend-engineer-test/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)

A Django REST Framework API for an e-commerce system with OpenID Connect authentication, hierarchical product categories, order management, and automated notifications.

## 🚀 Live Demo

**Base URL:** https://savvannah-assessment.onrender.com

**API Root:** https://savvannah-assessment.onrender.com/api/

**Admin Panel:** https://savvannah-assessment.onrender.com/admin/

## 📋 Features

- ✅ Customer, Product, and Order management
- ✅ REST API with Django REST Framework
- ✅ OpenID Connect authentication (Auth0)
- ✅ Hierarchical product categories (arbitrary depth)
- ✅ Order management with stock tracking
- ✅ SMS notifications via Africa's Talking
- ✅ Email notifications for administrators
- ✅ PostgreSQL database
- ✅ Docker containerization
- ✅ Kubernetes deployment ready
- ✅ CI/CD with GitHub Actions
- ✅ Comprehensive test coverage (85%+)

## 🔐 Quick Start - Testing the API

### For Reviewers: Pre-configured Test Account

A test account is ready to use immediately:

**Username:** `reviewer`  
**Password:** `Review2024!`

This account includes:
- Full customer profile (phone number, address)
- Ready for order creation
- Automatically created on deployment

### Step 1: Obtain Authentication Token

```bash
curl -X POST https://savvannah-assessment.onrender.com/api/obtain-token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"reviewer","password":"Review2024!"}'
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "username": "reviewer",
  "email": "reviewer@savannah.test"
}
```

### Step 2: Use Token in API Requests

```bash
# Get all products
curl https://savvannah-assessment.onrender.com/api/products/

# Get user's orders (authenticated)
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  https://savvannah-assessment.onrender.com/api/orders/

# Create an order
curl -X POST https://savvannah-assessment.onrender.com/api/orders/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

## 📚 API Endpoints

### Public Endpoints (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | API root with endpoint list |
| GET | `/api/categories/` | List all categories |
| GET | `/api/categories/{id}/` | Get specific category |
| GET | `/api/categories/{id}/average_price/` | Average price for category and descendants |
| GET | `/api/products/` | List all products |
| GET | `/api/products/{id}/` | Get specific product |

### Authenticated Endpoints (Token Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/obtain-token/` | Get authentication token |
| GET | `/api/orders/` | List user's orders |
| POST | `/api/orders/` | Create new order |
| GET | `/api/orders/{id}/` | Get specific order |
| POST | `/api/categories/` | Create category (requires customer) |
| POST | `/api/products/` | Create product (requires customer) |

### Authentication

All authenticated endpoints require the `Authorization` header:

```
Authorization: Token YOUR_TOKEN_HERE
```

## 🏗️ Architecture & Tech Stack

### Technology Stack

- **Backend:** Python, Django 5.2, Django REST Framework 3.16
- **Database:** PostgreSQL 15
- **Authentication:** OpenID Connect (Auth0) + Token Authentication
- **Notifications:** Africa's Talking SMS, Django Email
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Testing:** pytest, pytest-django, Playwright
- **Code Quality:** flake8, black, isort

### Database Schema

```
User (Django built-in)
  ↓ (one-to-one)
Customer
  ├── phone_number
  ├── address
  └── orders[]

Category (hierarchical)
  ├── name
  ├── parent (self-referential FK)
  ├── children[]
  └── products[]

Product
  ├── name
  ├── description
  ├── price
  ├── stock
  └── category (FK)

Order
  ├── customer (FK)
  ├── created_at
  ├── total_amount
  └── items[]

OrderItem
  ├── order (FK)
  ├── product (FK)
  └── quantity
```

### Key Features Implementation

**Hierarchical Categories:**
- Arbitrary depth category trees
- Efficient descendant retrieval (non-recursive algorithm)
- Average price calculation includes all subcategories

**Order Processing:**
- Atomic transactions for stock management
- Automatic customer profile creation
- Real-time stock validation
- SMS confirmation to customer
- Email notification to admin

**Authentication:**
- OpenID Connect (Auth0) for web login
- Token authentication for API access
- Permission-based access control

## 💻 Local Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Docker (optional)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/savannah-backend-engineer-test.git
cd savannah-backend-engineer-test
```

2. **Create and activate virtual environment**
```bash
# Create virtualenv
python -m venv venv

# Activate on Mac/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load sample data (optional)**
```bash
python manage.py loaddata api/fixtures/products.json
```

8. **Start the development server**
```bash
# Default port 8000
python manage.py runserver

# Custom port (e.g., 8888)
python manage.py runserver 8888
```

Visit: http://localhost:8000/api/ (or your custom port)

**Note:** The application is also deployed at https://savvannah-assessment.onrender.com


🧪 RUNNING TESTS

This project uses pytest with pytest-django and Playwright for end-to-end (E2E) and integration testing.

1. Environment Setup

Before running tests, make sure you are inside the virtual environment:

**source venv/bin/activate**


Using the Test Runner Script (Recommended)

I have provide a helper script **runtests.sh** to handle environment variables automatically.

Make it executable (first time only):
**chmod +x runtests.sh**

RUN ALL TESTS

### ./runtests.sh tests/ -v

./runtests.sh tests/e2e -v                  # Run all E2E tests
./runtests.sh tests/integration -v          # Run integration tests
./runtests.sh tests/unit -v                 # Run unit tests
./runtests.sh tests/e2e/tests/orders/test_orders_business.py::test_orders_sorted_by_created_date -v



3. Running Tests Manually (Without Script)

If you don’t want to use runtests.sh, you must export the variables yourself:

export PYTHONPATH=$PYTHONPATH:$(pwd)
export DJANGO_SETTINGS_MODULE=savannah_assess.settings
pytest tests/ -v


4. Coverage Reports

To run tests with coverage:

### ./runtests.sh --cov=api tests/ -v

✅ With this setup, you can easily run unit tests, integration tests, and end-to-end tests without worrying about environment setup.





## 🎨 Code Quality & Linting

This project uses flake8, black, and isort for consistent code style.

### Install linting tools:
```bash
pip install black flake8 isort
```

### Run linting:
```bash
# Check code style
flake8 .

# Format code automatically
black .

# Sort imports
isort .
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t savannah-api .

# Run container
docker run -p 8888:8888 --env-file .env savannah-api
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Stop services
docker-compose down
```

## ☸️ Kubernetes Deployment

For detailed Kubernetes deployment instructions, see [K8S.md](./K8S.md)
```

## 📊 CI/CD Pipeline

GitHub Actions workflow includes:

1. **Linting:** flake8, black, isort
2. **Unit Tests:** Isolated component tests
3. **Integration Tests:** API endpoint tests
4. **E2E Tests:** Full workflow tests with Playwright
5. **Coverage Reporting:** Codecov integration
6. **Docker Build:** Automated image build and push

View workflow: `.github/workflows/django-ci.yml`

## 🔧 Management Commands

```bash
# Create API token for user
python manage.py create_token <username>

# Example:
python manage.py create_token reviewer

# Create superuser if not exists (for deployments)
python manage.py createsuperuserifnotexists
```

**Note:** The `/api/obtain-token/` endpoint is the recommended method for obtaining tokens in production, as it works without server access.


## 🚨 Known Limitations

- SMS notifications use sandbox mode (requires Africa's Talking production account)
- Email notifications use console backend in development

## 📝 Project Structure

```
savannah_assessment/
├── api/                        # Main application
│   ├── management/
│   │   └── commands/          # Custom management commands
│   ├── migrations/            # Database migrations
│   ├── fixtures/              # Sample data
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── permissions.py         # Custom permissions
│   └── notifications.py       # SMS/Email logic
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── k8s/                       # Kubernetes manifests
├── .github/workflows/         # CI/CD pipelines
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Local development
├── requirements.txt           # Python dependencies
├── K8S.md                     # Kubernetes guide
└── manage.py                  # Django management script
```

## 👥 Author

**Stephen Owin**
- Email: stephenowin233@gmail.com
- GitHub: https://github.com/stephenOwino

## 📄 License

This project was created as part of a technical assessment for Savannah Informatics.

## 🙏 Acknowledgments

- Savannah Informatics for the assessment opportunity
- Auth0 for authentication services
- Africa's Talking for SMS gateway
