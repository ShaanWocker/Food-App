# 🚀 Quick Start Guide

This guide will help you get the Food Ordering App up and running quickly.

## Prerequisites

Ensure you have:
- Python 3.10 or higher
- PostgreSQL 13 or higher
- pip package manager
- git

## Quick Installation (5 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/ShaanWocker/Food-App.git
cd Food-App

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Start PostgreSQL (if not running)
# Linux/Mac:
sudo systemctl start postgresql
# Or use homebrew on Mac:
brew services start postgresql

# Create database
createdb foodapp_db

# Or using psql:
psql -U postgres
CREATE DATABASE foodapp_db;
\q
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - defaults work for local development)
nano .env  # or use your favorite editor
```

**Minimum configuration for local development:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/foodapp_db
SECRET_KEY=your-secret-key-here
```

### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Load sample data
python init_db.py
```

This creates:
- Admin account: `admin@foodapp.com` / `AdminPass123!`
- Test user: `user@example.com` / `UserPass123!`
- 6 sample meals

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
./start_backend.sh
# Or manually:
uvicorn app.main:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs

**Terminal 2 - Frontend:**
```bash
./start_kivy.sh
# Or manually:
python kivy_app/main.py
```

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python init_db.py

# View logs
docker-compose logs -f
```

Services:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

## First Steps

1. **Test the API:**
   - Open http://localhost:8000/api/docs
   - Try the health check endpoint: GET `/health`

2. **Login to Kivy App:**
   - Use test account: `user@example.com` / `UserPass123!`
   - Browse the menu
   - Add items to cart

3. **Admin Dashboard:**
   - Login with: `admin@foodapp.com` / `AdminPass123!`
   - Manage meals and orders

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep foodapp
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Kivy Won't Start
```bash
# Linux: Set display backend
export KIVY_GL_BACKEND=gl

# Update Kivy
pip install --upgrade kivy kivymd
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [API Documentation](http://localhost:8000/api/docs)
- Explore the code structure
- Configure Stripe for payments (see README)
- Deploy to production (see README)

## Need Help?

- Check the [README.md](README.md) troubleshooting section
- Open an issue on GitHub
- Review API documentation at `/api/docs`

## Production Deployment

For production deployment:

1. Update `.env` with production values
2. Set `DEBUG=False`
3. Use a strong `SECRET_KEY`
4. Configure real Stripe keys
5. Set up proper database backups
6. Use HTTPS
7. Configure proper CORS origins

See [README.md](README.md) for detailed production deployment guide.

---

**Happy Coding! 🍽️**
