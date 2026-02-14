# Changelog

All notable changes to the Food Ordering Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-02-14

### 🔒 Security
- **CRITICAL:** Updated aiohttp from 3.9.1 to 3.13.3
  - Fixed HTTP Parser auto_decompress zip bomb vulnerability
  - Fixed Denial of Service when parsing malformed POST requests
  - Fixed directory traversal vulnerability
- **CRITICAL:** Updated python-multipart from 0.0.6 to 0.0.22
  - Fixed arbitrary file write vulnerability
  - Fixed DoS via malformed multipart/form-data boundary
  - Fixed Content-Type Header ReDoS vulnerability
- **HIGH:** Updated fastapi from 0.104.1 to 0.115.0
  - Fixed Content-Type Header ReDoS vulnerability
- **HIGH:** Updated Pillow from 10.1.0 to 12.1.1
  - Fixed buffer overflow vulnerability
  - Fixed out-of-bounds write when loading PSD images
- **MEDIUM:** Updated python-jose from 3.3.0 to 3.4.0
  - Fixed algorithm confusion with OpenSSH ECDSA keys

### Added
- SECURITY.md with comprehensive security policies
- Security best practices documentation
- Vulnerability reporting guidelines
- Production security checklist

### Verified
- ✅ All dependencies checked against GitHub Advisory Database
- ✅ No known vulnerabilities in current versions

## [1.0.0] - 2024-02-14

### Added
- Complete FastAPI backend with RESTful API
- SQLAlchemy models with PostgreSQL support
- JWT authentication with refresh tokens
- Stripe payment integration
- Shopping cart functionality
- Order management system
- Admin dashboard with analytics
- Kivy/KivyMD cross-platform frontend
- User registration and login screens
- Menu browsing and filtering
- Cart management UI
- Docker and Docker Compose support
- Database migrations with Alembic
- Comprehensive documentation (README, QUICKSTART, API_DOCS)
- Test suite structure with pytest
- Database initialization script with sample data
- Startup scripts for backend and frontend
- Mobile build configuration (buildozer.spec)

### Security
- Password hashing with bcrypt
- JWT token management
- Rate limiting on authentication endpoints
- Input validation with Pydantic
- SQL injection prevention via ORM
- CORS configuration

### Documentation
- Comprehensive README with setup instructions
- Quick start guide for developers
- Complete API documentation
- Implementation summary
- Troubleshooting guides

---

## Security Advisory Process

For security vulnerabilities, please refer to [SECURITY.md](SECURITY.md) for our security policy and reporting guidelines.

## Support

For questions or issues:
- Open an issue on GitHub
- Check documentation in README.md
- Review API docs at http://localhost:8000/api/docs
