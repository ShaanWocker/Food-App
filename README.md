# 🍽️ Food Ordering App

A complete production-ready kitchen/food ordering application built with FastAPI backend and Kivy frontend.

## ✨ Features

### 🔐 Authentication
- User registration with email validation
- Secure login with JWT tokens
- Password hashing with bcrypt
- Token refresh mechanism

### 🍕 Menu System
- Monthly rotating menu
- Browse available meals
- Filter by category, month, and availability
- High-quality meal images

### 🛒 Shopping Cart
- Add/remove items
- Update quantities
- Real-time price calculations
- Persistent cart storage

### 💳 Payment Processing
- Stripe integration
- Secure checkout
- Payment confirmation
- Order creation on successful payment

### 📦 Order Management
- View order history
- Real-time order tracking
- Order status updates
- Detailed order information

### 👨‍💼 Admin Dashboard
- Menu management (CRUD operations)
- Order management
- Revenue analytics
- Popular meals statistics
- User management

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async API framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM with Alembic migrations
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Stripe** - Payment processing

### Frontend
- **Kivy** - Cross-platform Python framework
- **KivyMD** - Material Design components
- **Requests** - HTTP client

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Stripe account (for payments)
- pip package manager

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ShaanWocker/Food-App.git
cd Food-App
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://foodapp:foodapp123@localhost:5432/foodapp_db

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 5. Set Up Database

Create PostgreSQL database:

```bash
createdb foodapp_db
```

Or using psql:

```sql
CREATE DATABASE foodapp_db;
CREATE USER foodapp WITH PASSWORD 'foodapp123';
GRANT ALL PRIVILEGES ON DATABASE foodapp_db TO foodapp;
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

## 🏃 Running the Application

### Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Start Kivy Frontend

```bash
python kivy_app/main.py
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

### Manual Docker Build

```bash
# Build image
docker build -t foodapp-backend .

# Run container
docker run -p 8000:8000 --env-file .env foodapp-backend
```

## 📱 Building for Mobile

### Android

1. Install buildozer:

```bash
pip install buildozer
```

2. Initialize buildozer:

```bash
cd kivy_app
buildozer init
```

3. Build APK:

```bash
buildozer -v android debug
```

### iOS

Requires macOS and Xcode:

```bash
# Install kivy-ios
pip install kivy-ios

# Build
toolchain build kivy

# Create Xcode project
toolchain create FoodApp kivy_app/main.py
```

## 🧪 Testing

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 📚 API Documentation

### Authentication Endpoints

```
POST /api/v1/auth/register - Register new user
POST /api/v1/auth/login - User login
POST /api/v1/auth/refresh - Refresh access token
```

### Meals Endpoints

```
GET  /api/v1/meals/ - List meals (with filters)
GET  /api/v1/meals/{id} - Get meal details
POST /api/v1/meals/ - Create meal (admin)
PUT  /api/v1/meals/{id} - Update meal (admin)
DELETE /api/v1/meals/{id} - Delete meal (admin)
```

### Cart Endpoints

```
GET  /api/v1/cart/ - Get user cart
POST /api/v1/cart/items - Add item to cart
PUT  /api/v1/cart/items/{id} - Update cart item
DELETE /api/v1/cart/items/{id} - Remove from cart
DELETE /api/v1/cart/ - Clear cart
```

### Order Endpoints

```
GET  /api/v1/orders/ - List user orders
GET  /api/v1/orders/{id} - Get order details
POST /api/v1/orders/ - Create order from cart
```

### Payment Endpoints

```
POST /api/v1/payments/create-payment-intent - Create Stripe payment
POST /api/v1/payments/create-checkout-session - Create checkout session
POST /api/v1/payments/confirm-payment - Confirm payment
POST /api/v1/payments/webhook - Stripe webhook handler
```

### Admin Endpoints

```
GET  /api/v1/admin/orders - List all orders
GET  /api/v1/admin/orders/{id} - Get order details
PATCH /api/v1/admin/orders/{id}/status - Update order status
GET  /api/v1/admin/analytics/revenue - Revenue analytics
GET  /api/v1/admin/analytics/popular-meals - Popular meals stats
```

## 🔑 Default Admin Account

After first run, create an admin account manually in the database or use the provided script:

```python
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email="admin@foodapp.com",
    username="admin",
    full_name="Admin User",
    password_hash=get_password_hash("AdminPass123!"),
    is_admin=True
)
db.add(admin)
db.commit()
```

## 🗂️ Project Structure

```
food-app/
├── app/                    # FastAPI backend
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── api/               # API routes
│   ├── core/              # Core utilities
│   ├── services/          # Business logic
│   ├── middleware/        # Custom middleware
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   └── main.py            # FastAPI app
│
├── kivy_app/              # Kivy frontend
│   ├── screens/           # App screens
│   ├── components/        # Reusable components
│   ├── services/          # API client services
│   ├── utils/             # Utility functions
│   └── main.py            # Kivy app entry
│
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
├── docker-compose.yml     # Docker setup
├── Dockerfile            # Docker image
└── README.md             # This file
```

## 🔧 Development

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

### Code Quality

Format code:

```bash
black app/ kivy_app/
```

Lint code:

```bash
flake8 app/ kivy_app/
```

Type checking:

```bash
mypy app/
```

## 🐛 Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

2. Check database exists:
```bash
psql -l
```

3. Test connection:
```bash
psql -U foodapp -d foodapp_db
```

### Kivy Issues

1. If Kivy doesn't start, ensure dependencies are installed:
```bash
pip install --upgrade kivy kivymd
```

2. For display issues on Linux:
```bash
export KIVY_GL_BACKEND=gl
```

### API Issues

1. Check logs:
```bash
docker-compose logs backend
```

2. Verify environment variables:
```bash
env | grep DATABASE_URL
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@foodapp.com

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- Kivy team for cross-platform support
- Stripe for payment processing
- PostgreSQL for reliable data storage

## 🔄 Updates

### Version 1.0.0 (Current)
- ✅ User authentication
- ✅ Menu browsing
- ✅ Shopping cart
- ✅ Order management
- ✅ Stripe payments
- ✅ Admin dashboard

### Upcoming Features
- 📧 Email notifications
- 📱 Push notifications
- 🗺️ Google Maps integration
- 📊 Advanced analytics
- 🌐 Multi-language support
- 🎨 Theme customization
