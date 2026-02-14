# 📚 API Documentation

Complete API reference for the Food Ordering Application.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require authentication using JWT Bearer tokens.

Include the token in the Authorization header:
```
Authorization: Bearer <your-token-here>
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "phone_number": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK` (same as login)

---

## 🍕 Meal Endpoints

### List Meals
```http
GET /meals/?month=1&year=2024&is_available=true&category=Pizza
```

**Query Parameters:**
- `month` (optional): Filter by month (1-12)
- `year` (optional): Filter by year
- `is_available` (optional): Filter by availability
- `category` (optional): Filter by category
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Page size (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Margherita Pizza",
    "description": "Fresh mozzarella and basil",
    "price": "14.99",
    "image_url": "https://example.com/pizza.jpg",
    "available_month": "2024-01-01",
    "is_available": true,
    "category": "Pizza",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### Get Meal
```http
GET /meals/{meal_id}
```

**Response:** `200 OK` (single meal object)

### Create Meal (Admin Only)
```http
POST /meals/
```

**Request Body:**
```json
{
  "name": "New Pizza",
  "description": "Delicious pizza",
  "price": "15.99",
  "image_url": "https://example.com/pizza.jpg",
  "available_month": "2024-01-01",
  "is_available": true,
  "category": "Pizza"
}
```

**Response:** `201 Created` (meal object)

### Update Meal (Admin Only)
```http
PUT /meals/{meal_id}
```

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Pizza",
  "price": "16.99",
  "is_available": false
}
```

**Response:** `200 OK` (updated meal object)

### Delete Meal (Admin Only)
```http
DELETE /meals/{meal_id}
```

**Response:** `204 No Content`

---

## 🛒 Cart Endpoints

### Get Cart
```http
GET /cart/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "meal_id": "uuid",
      "quantity": 2,
      "meal": {
        "id": "uuid",
        "name": "Margherita Pizza",
        "price": "14.99"
      }
    }
  ],
  "subtotal": "29.98",
  "tax": "2.40",
  "total": "32.38"
}
```

### Add to Cart
```http
POST /cart/items
```

**Request Body:**
```json
{
  "meal_id": "uuid",
  "quantity": 2
}
```

**Response:** `201 Created` (cart item object)

### Update Cart Item
```http
PUT /cart/items/{item_id}
```

**Request Body:**
```json
{
  "quantity": 3
}
```

**Response:** `200 OK` (updated cart item)

### Remove from Cart
```http
DELETE /cart/items/{item_id}
```

**Response:** `204 No Content`

### Clear Cart
```http
DELETE /cart/
```

**Response:** `204 No Content`

---

## 📦 Order Endpoints

### Create Order
```http
POST /orders/
```

**Request Body:**
```json
{
  "delivery_address_id": "uuid",
  "special_instructions": "Ring doorbell twice"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "total_price": "32.38",
  "delivery_address_id": "uuid",
  "payment_status": "Pending",
  "order_status": "Pending",
  "special_instructions": "Ring doorbell twice",
  "created_at": "2024-01-01T00:00:00",
  "order_items": [...],
  "delivery_address": {...}
}
```

### List Orders
```http
GET /orders/
```

**Response:** `200 OK` (array of order objects)

### Get Order
```http
GET /orders/{order_id}
```

**Response:** `200 OK` (order object)

---

## 💳 Payment Endpoints

### Create Payment Intent
```http
POST /payments/create-payment-intent?order_id={order_id}
```

**Response:** `200 OK`
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx",
  "amount": "32.38",
  "currency": "usd"
}
```

### Create Checkout Session
```http
POST /payments/create-checkout-session
```

**Request Body:**
```json
{
  "order_id": "uuid",
  "success_url": "https://example.com/success",
  "cancel_url": "https://example.com/cancel"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "cs_xxx",
  "url": "https://checkout.stripe.com/..."
}
```

### Confirm Payment
```http
POST /payments/confirm-payment
```

**Request Body:**
```json
{
  "order_id": "uuid",
  "payment_intent_id": "pi_xxx"
}
```

**Response:** `200 OK`
```json
{
  "message": "Payment confirmed successfully"
}
```

---

## 👨‍💼 Admin Endpoints

### List All Orders
```http
GET /admin/orders?status=Pending
```

**Query Parameters:**
- `status` (optional): Filter by order status
- `skip`, `limit`: Pagination

**Response:** `200 OK` (array of orders)

### Update Order Status
```http
PATCH /admin/orders/{order_id}/status
```

**Request Body:**
```json
{
  "order_status": "Preparing"
}
```

**Values:** `Pending`, `Preparing`, `Out for Delivery`, `Delivered`, `Cancelled`

**Response:** `200 OK` (updated order)

### Revenue Analytics
```http
GET /admin/analytics/revenue?days=30
```

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "total_revenue": 1250.50,
  "total_orders": 45,
  "average_order_value": 27.79,
  "orders_by_status": {
    "Pending": 5,
    "Preparing": 3,
    "Delivered": 35,
    "Cancelled": 2
  }
}
```

### Popular Meals
```http
GET /admin/analytics/popular-meals?limit=10
```

**Response:** `200 OK`
```json
[
  {
    "meal_id": "uuid",
    "meal_name": "Margherita Pizza",
    "total_ordered": 120
  }
]
```

---

## 👤 User Profile Endpoints

### Get Profile
```http
GET /users/me
```

**Response:** `200 OK` (user object)

### Update Profile
```http
PUT /users/me
```

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "phone_number": "+1987654321"
}
```

**Response:** `200 OK` (updated user)

### List Addresses
```http
GET /users/me/addresses
```

**Response:** `200 OK` (array of addresses)

### Add Address
```http
POST /users/me/addresses
```

**Request Body:**
```json
{
  "street_address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "additional_instructions": "Apt 4B",
  "is_default": true
}
```

**Response:** `201 Created` (address object)

---

## Error Responses

All endpoints may return these error codes:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Interactive Documentation

For interactive API documentation, visit:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

These interfaces allow you to test endpoints directly in your browser.
