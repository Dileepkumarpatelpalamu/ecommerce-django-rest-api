```markdown
# E-commerce API Documentation

## Introduction

The E-commerce API is a RESTful API built with Django REST Framework (DRF) for managing an online shopping platform. It supports user registration, product browsing, cart management, checkout, and order tracking, similar to platforms like Flipkart. The API uses JSON Web Tokens (JWT) for authentication, MySQL as the database, and includes public and authenticated endpoints.

### Features
- **User Management**: Register, login, and manage user profiles.
- **Category/Product Browsing**: View, search, and filter categories and products.
- **Wishlist**: Add/remove products to/from a wishlist.
- **Cart**: Add, update, or remove items in a shopping cart.
- **Checkout**: Validate cart, preview costs, and place orders with coupons.
- **Order Management**: View, cancel, return, or refund orders.
- **Public Access**: Search and browse categories/products without authentication.
- **Admin Interface**: Manage categories and products via `/admin/` (superuser only).

### Base URL
`http://localhost:8000/api/` (adjust for production host).

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Installation
1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository_url>
   cd ecommerce_drf_api
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt pillow mysqlclient
   ```

4. **Configure MySQL**:
   - Start MySQL: `sudo service mysql start` (Ubuntu).
   - Create a database:
     ```sql
     mysql -u root -p
     CREATE DATABASE ecommerce_db;
     EXIT;
     ```
   - Update `ecommerce_api/ecommerce/settings.py` with your MySQL credentials:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'ecommerce_db',
             'USER': 'your_mysql_user',
             'PASSWORD': 'your_mysql_password',
             'HOST': 'localhost',
             'PORT': '3306',
             'OPTIONS': {
                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
             },
         }
     }
     ```

5. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
   - Example: `username=admin`, `email=admin@example.com`, `password=Admin123`.

7. **Run the Server**:
   ```bash
   python manage.py runserver
   ```
   - Access the API at `http://localhost:8000/api/`.
   - Admin panel: `http://localhost:8000/admin/`.

## Authentication

The API uses JWT for authentication. Most endpoints require an `Authorization` header with a Bearer token, except for public endpoints (e.g., `/api/register/`, `/api/products/search/`).

### Obtaining Tokens
1. **Register a User**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "Test1234"}' \
     http://localhost:8000/api/register/
   ```
   - Response (201 Created):
     ```json
     {
         "id": 1,
         "username": "testuser",
         "email": "test@example.com"
     }
     ```

2. **Login to Get Tokens**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "Test1234"}' \
     http://localhost:8000/api/login/
   ```
   - Response (200 OK):
     ```json
     {
         "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
         "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
     }
     ```

3. **Use Access Token**:
   - Include in headers for authenticated requests:
     ```bash
     Authorization: Bearer <access_token>
     ```
   - Example:
     ```bash
     curl -X GET -H "Authorization: Bearer <access_token>" \
       http://localhost:8000/api/profile/
     ```

4. **Refresh Token**:
   - If the access token expires (60 minutes), use the refresh token (valid for 1 day):
     ```bash
     curl -X POST -H "Content-Type: application/json" \
       -d '{"refresh": "<refresh_token>"}' \
       http://localhost:8000/api/token/refresh/
     ```
   - Response:
     ```json
     {
         "access": "<new_access_token>"
     }
     ```

## Endpoints

Below is a list of all API endpoints, grouped by resource. Each endpoint includes the HTTP method, URL, parameters, authentication requirements, and example requests/responses.

### User Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/register/` | POST | Register a new user | None | AllowAny |
| `/login/` | POST | Login and obtain JWT tokens | None | AllowAny |
| `/profile/` | GET, PATCH | Retrieve or update user profile | JWT | IsAuthenticated |

#### Register (`/register/`)
- **Method**: POST
- **URL**: `/api/register/`
- **Body**:
  ```json
  {
      "username": "string",
      "email": "string",
      "password": "string"
  }
  ```
- **Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"username": "newuser", "email": "newuser@example.com", "password": "NewPass123"}' \
    http://localhost:8000/api/register/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 2,
      "username": "newuser",
      "email": "newuser@example.com"
  }
  ```
- **Error Response** (400):
  ```json
  {
      "username": ["This username is already taken."]
  }
  ```

#### Login (`/login/`)
- **Method**: POST
- **URL**: `/api/login/`
- **Body**:
  ```json
  {
      "username": "string",
      "password": "string"
  }
  ```
- **Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"username": "newuser", "password": "NewPass123"}' \
    http://localhost:8000/api/login/
  ```
- **Success Response** (200):
  ```json
  {
      "refresh": "<refresh_token>",
      "access": "<access_token>"
  }
  ```
- **Error Response** (401):
  ```json
  {
      "error": "Invalid credentials"
  }
  ```

#### User Profile (`/profile/`)
- **Method**: GET, PATCH
- **URL**: `/api/profile/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **PATCH Body** (optional fields):
  ```json
  {
      "username": "string",
      "email": "string",
      "password": "string"
  }
  ```
- **Example (GET)**:
  ```bash
  curl -X GET -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/profile/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 2,
      "username": "newuser",
      "email": "newuser@example.com"
  }
  ```
- **Example (PATCH)**:
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"email": "updated@example.com"}' \
    http://localhost:8000/api/profile/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 2,
      "username": "newuser",
      "email": "updated@example.com"
  }
  ```

### Category Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/categories/` | GET, POST | List or create categories | GET: None, POST: JWT | IsAuthenticatedOrReadOnly |
| `/categories/<id>/` | GET, PUT, DELETE | Retrieve, update, or delete a category | GET: None, Others: JWT | IsAuthenticatedOrReadOnly |
| `/categories/search/` | GET | Search categories by name/description | None | AllowAny |

#### List/Create Categories (`/categories/`)
- **Method**: GET, POST
- **URL**: `/api/categories/`
- **POST Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **POST Body**:
  ```json
  {
      "name": "string",
      "description": "string"
  }
  ```
- **Example (GET)**:
  ```bash
  curl -X GET http://localhost:8000/api/categories/
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "name": "Electronics",
          "description": "Electronic gadgets"
      }
  ]
  ```
- **Example (POST)**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"name": "Books", "description": "All kinds of books"}' \
    http://localhost:8000/api/categories/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 2,
      "name": "Books",
      "description": "All kinds of books"
  }
  ```

#### Category Detail (`/categories/<id>/`)
- **Method**: GET, PUT, DELETE
- **URL**: `/api/categories/<id>/`
- **PUT Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **PUT Body**:
  ```json
  {
      "name": "string",
      "description": "string"
  }
  ```
- **Example (GET)**:
  ```bash
  curl -X GET http://localhost:8000/api/categories/1/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic gadgets"
  }
  ```
- **Example (PUT)**:
  ```bash
  curl -X PUT -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"name": "Electronics Updated", "description": "Updated gadgets"}' \
    http://localhost:8000/api/categories/1/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "name": "Electronics Updated",
      "description": "Updated gadgets"
  }
  ```

#### Search Categories (`/categories/search/`)
- **Method**: GET
- **URL**: `/api/categories/search/?search=<query>`
- **Query Parameters**:
  - `search`: String to search in `name` or `description`.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/categories/search/?search=electronics"
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "name": "Electronics",
          "description": "Electronic gadgets"
      }
  ]
  ```

### Product Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/products/` | GET, POST | List or create products | GET: None, POST: JWT | IsAuthenticatedOrReadOnly |
| `/products/<id>/` | GET, PUT, DELETE | Retrieve, update, or delete a product | GET: None, Others: JWT | IsAuthenticatedOrReadOnly |
| `/products/search/` | GET | Search products by name/description | None | AllowAny |
| `/products/filter/` | GET | Filter products by category | None | AllowAny |

#### List/Create Products (`/products/`)
- **Method**: GET, POST
- **URL**: `/api/products/`
- **POST Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **POST Body** (multipart/form-data for image):
  ```json
  {
      "name": "string",
      "description": "string",
      "price": "decimal",
      "stock": "integer",
      "category_id": "integer",
      "image": "file" (optional)
  }
  ```
- **Example (GET)**:
  ```bash
  curl -X GET http://localhost:8000/api/products/
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "name": "Laptop",
          "description": "High-end laptop",
          "price": "999.99",
          "stock": 10,
          "category": {
              "id": 1,
              "name": "Electronics",
              "description": "Electronic gadgets"
          },
          "image": "/media/products/laptop.jpg",
          "created_at": "2025-06-14T00:00:00Z"
      }
  ]
  ```
- **Example (POST)**:
  ```bash
  curl -X POST -H "Authorization: Bearer <access_token>" \
    -F "name=Smartphone" \
    -F "description=Latest smartphone" \
    -F "price=699.99" \
    -F "stock=20" \
    -F "category_id=1" \
    -F "image=@/path/to/image.jpg" \
    http://localhost:8000/api/products/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 2,
      "name": "Smartphone",
      "description": "Latest smartphone",
      "price": "699.99",
      "stock": 20,
      "category": {
          "id": 1,
          "name": "Electronics",
          "description": "Electronic gadgets"
      },
      "image": "/media/products/smartphone.jpg",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```

#### Product Detail (`/products/<id>/`)
- **Method**: GET, PUT, DELETE
- **URL**: `/api/products/<id>/`
- **PUT Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **PUT Body** (multipart/form-data):
  ```json
  {
      "name": "string",
      "description": "string",
      "price": "decimal",
      "stock": "integer",
      "category_id": "integer",
      "image": "file" (optional)
  }
  ```
- **Example (GET)**:
  ```bash
  curl -X GET http://localhost:8000/api/products/1/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "name": "Laptop",
      "description": "High-end laptop",
      "price": "999.99",
      "stock": 10,
      "category": {
          "id": 1,
          "name": "Electronics",
          "description": "Electronic gadgets"
      },
      "image": "/media/products/laptop.jpg",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```

#### Search Products (`/products/search/`)
- **Method**: GET
- **URL**: `/api/products/search/?search=<query>`
- **Query Parameters**:
  - `search`: String to search in `name` or `description`.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/products/search/?search=laptop"
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "name": "Laptop",
          "description": "High-end laptop",
          "price": "999.99",
          "stock": 10,
          "category": {
              "id": 1,
              "name": "Electronics",
              "description": "Electronic gadgets"
          },
          "image": "/media/products/laptop.jpg",
          "created_at": "2025-06-14T00:00:00Z"
      }
  ]
  ```

#### Filter Products by Category (`/products/filter/`)
- **Method**: GET
- **URL**: `/api/products/filter/?category_id=<id>`
- **Query Parameters**:
  - `category_id`: Integer ID of the category.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/products/filter/?category_id=1"
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "name": "Laptop",
          "description": "High-end laptop",
          "price": "999.99",
          "stock": 10,
          "category": {
              "id": 1,
              "name": "Electronics",
              "description": "Electronic gadgets"
          },
          "image": "/media/products/laptop.jpg",
          "created_at": "2025-06-14T00:00:00Z"
      }
  ]
  ```

### Address Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/addresses/` | GET, POST | List or create addresses | JWT | IsAuthenticated |
| `/addresses/<id>/` | GET, PUT, DELETE | Retrieve, update, or delete an address | JWT | IsAuthenticated |

#### List/Create Addresses (`/addresses/`)
- **Method**: GET, POST
- **URL**: `/api/addresses/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **POST Body**:
  ```json
  {
      "name": "string",
      "street": "string",
      "city": "string",
      "state": "string",
      "postal_code": "string",
      "country": "string",
      "is_default": "boolean"
  }
  ```
- **Example (POST)**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"name": "John Doe", "street": "123 Main St", "city": "New York", "state": "NY", "postal_code": "10001", "country": "USA", "is_default": true}' \
    http://localhost:8000/api/addresses/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 1,
      "name": "John Doe",
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA",
      "is_default": true
  }
  ```

### Wishlist Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/wishlist/` | GET, POST | List or add wishlist items | JWT | IsAuthenticated |
| `/wishlist/<id>/delete/` | DELETE | Remove a wishlist item | JWT | IsAuthenticated |

#### List/Add Wishlist Items (`/wishlist/`)
- **Method**: GET, POST
- **URL**: `/api/wishlist/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **POST Body**:
  ```json
  {
      "product_id": "integer"
  }
  ```
- **Example (POST)**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"product_id": 1}' \
    http://localhost:8000/api/wishlist/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 1,
      "product": {
          "id": 1,
          "name": "Laptop",
          "description": "High-end laptop",
          "price": "999.99",
          "stock": 10,
          "category": {
              "id": 1,
              "name": "Electronics",
              "description": "Electronic gadgets"
          },
          "image": "/media/products/laptop.jpg",
          "created_at": "2025-06-14T00:00:00Z"
      },
      "added_at": "2025-06-14T00:00:00Z"
  }
  ```

### Cart Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/cart/` | GET | View cart details | JWT | IsAuthenticated |
| `/cart/add/` | POST | Add item to cart | JWT | IsAuthenticated |
| `/cart/items/<item_id>/` | PATCH | Update cart item quantity | JWT | IsAuthenticated |
| `/cart/items/<id>/delete/` | DELETE | Remove cart item | JWT | IsAuthenticated |
| `/cart/clear/` | DELETE | Clear all cart items | JWT | IsAuthenticated |

#### View Cart (`/cart/`)
- **Method**: GET
- **URL**: `/api/cart/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Example**:
  ```bash
  curl -X GET -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/cart/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "user": 2,
      "items": [
          {
              "id": 1,
              "product": {
                  "id": 1,
                  "name": "Laptop",
                  "description": "High-end laptop",
                  "price": "999.99",
                  "stock": 10,
                  "category": {
                      "id": 1,
                      "name": "Electronics",
                      "description": "Electronic gadgets"
                  },
                  "image": "/media/products/laptop.jpg",
                  "created_at": "2025-06-14T00:00:00Z"
              },
              "quantity": 2
          }
      ],
      "total_amount": "1999.98",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```

#### Add Item to Cart (`/cart/add/`)
- **Method**: POST
- **URL**: `/api/cart/add/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Body**:
  ```json
  {
      "product_id": "integer",
      "quantity": "integer"
  }
  ```
- **Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"product_id": 1, "quantity": 2}' \
    http://localhost:8000/api/cart/add/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 1,
      "product": {
          "id": 1,
          "name": "Laptop",
          "description": "High-end laptop",
          "price": "999.99",
          "stock": 10,
          "category": {
              "id": 1,
              "name": "Electronics",
              "description": "Electronic gadgets"
          },
          "image": "/media/products/laptop.jpg",
          "created_at": "2025-06-14T00:00:00Z"
      },
      "quantity": 2
  }
  ```
- **Error Response** (400):
  ```json
  {
      "error": "Insufficient stock"
  }
  ```

### Checkout

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/checkout/preview/` | POST | Preview checkout with coupon | JWT | IsAuthenticated |
| `/checkout/validate/` | POST | Validate cart for checkout | JWT | IsAuthenticated |
| `/checkout/` | POST | Place an order | JWT | IsAuthenticated |

#### Checkout Preview (`/checkout/preview/`)
- **Method**: POST
- **URL**: `/api/checkout/preview/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Body**:
  ```json
  {
      "coupon_code": "string" (optional)
  }
  ```
- **Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"coupon_code": "SALE10"}' \
    http://localhost:8000/api/checkout/preview/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "user": 2,
      "items": [
          {
              "id": 1,
              "product": {
                  "id": 1,
                  "name": "Laptop",
                  "description": "High-end laptop",
                  "price": "999.99",
                  "stock": 10,
                  "category": {
                      "id": 1,
                      "name": "Electronics",
                      "description": "Electronic gadgets"
                  },
                  "image": "/media/products/laptop.jpg",
                  "created_at": "2025-06-14T00:00:00Z"
              },
              "quantity": 2
          }
      ],
      "total_amount": "1999.98",
      "coupon_code": "SALE10",
      "discount_applied": "199.99",
      "tax": "180.00",
      "shipping_cost": "10.00",
      "grand_total": "1989.99",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```

#### Place Order (`/checkout/`)
- **Method**: POST
- **URL**: `/api/checkout/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Body**:
  ```json
  {
      "shipping_address_id": "integer",
      "billing_address_id": "integer",
      "payment_reference": "string" (optional),
      "coupon_code": "string" (optional)
  }
  ```
- **Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <access_token>" \
    -d '{"shipping_address_id": 1, "billing_address_id": 1, "payment_reference": "PAY123", "coupon_code": "SALE10"}' \
    http://localhost:8000/api/checkout/
  ```
- **Success Response** (201):
  ```json
  {
      "id": 1,
      "user": 2,
      "total_amount": "1989.99",
      "status": "pending",
      "items": [
          {
              "id": 1,
              "product": {
                  "id": 1,
                  "name": "Laptop",
                  "description": "High-end laptop",
                  "price": "999.99",
                  "stock": 8,
                  "category": {
                      "id": 1,
                      "name": "Electronics",
                      "description": "Electronic gadgets"
                  },
                  "image": "/media/products/laptop.jpg",
                  "created_at": "2025-06-14T00:00:00Z"
              },
              "quantity": 2,
              "price": "999.99"
          }
      ],
      "shipping_address": "John Doe, 123 Main St, New York",
      "billing_address": "John Doe, 123 Main St, New York",
      "payment_reference": "PAY123",
      "coupon": {
          "id": 1,
          "code": "SALE10",
          "discount_percentage": "10.00",
          "max_discount": null,
          "expiry_date": "2025-12-31T23:59:59Z",
          "is_active": true
      },
      "discount_applied": "199.99",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```
- **Error Response** (400):
  ```json
  {
      "error": "Payment failed"
  }
  ```

### Order Management

| Endpoint | Method | Description | Authentication | Permissions |
|----------|--------|-------------|----------------|-------------|
| `/orders/history/` | GET | List user orders | JWT | IsAuthenticated |
| `/orders/<id>/` | GET, PATCH | Retrieve or update order | JWT | IsAuthenticated |
| `/orders/<order_id>/cancel/` | POST | Cancel an order | JWT | IsAuthenticated |
| `/orders/<order_id>/return/` | POST | Return an order | JWT | IsAuthenticated |
| `/orders/<order_id>/refund/` | POST | Refund an order | JWT | IsAuthenticated |
| `/orders/items/<id>/` | GET | Retrieve order item details | JWT | IsAuthenticated |

#### List Orders (`/orders/history/`)
- **Method**: GET
- **URL**: `/api/orders/history/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Example**:
  ```bash
  curl -X GET -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/orders/history/
  ```
- **Success Response** (200):
  ```json
  [
      {
          "id": 1,
          "user": 2,
          "total_amount": "1989.99",
          "status": "pending",
          "items": [
              {
                  "id": 1,
                  "product": {
                      "id": 1,
                      "name": "Laptop",
                      "description": "High-end laptop",
                      "price": "999.99",
                      "stock": 8,
                      "category": {
                          "id": 1,
                          "name": "Electronics",
                          "description": "Electronic gadgets"
                      },
                      "image": "/media/products/laptop.jpg",
                      "created_at": "2025-06-14T00:00:00Z"
                  },
                  "quantity": 2,
                  "price": "999.99"
              }
          ],
          "shipping_address": "John Doe, 123 Main St, New York",
          "billing_address": "John Doe, 123 Main St, New York",
          "payment_reference": "PAY123",
          "coupon": {
              "id": 1,
              "code": "SALE10",
              "discount_percentage": "10.00",
              "max_discount": null,
              "expiry_date": "2025-12-31T23:59:59Z",
              "is_active": true
          },
          "discount_applied": "199.99",
          "created_at": "2025-06-14T00:00:00Z"
      }
  ]
  ```

#### Cancel Order (`/orders/<order_id>/cancel/`)
- **Method**: POST
- **URL**: `/api/orders/<order_id>/cancel/`
- **Headers**:
  ```bash
  Authorization: Bearer <access_token>
  ```
- **Example**:
  ```bash
  curl -X POST -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/orders/1/cancel/
  ```
- **Success Response** (200):
  ```json
  {
      "id": 1,
      "user": 2,
      "total_amount": "1989.99",
      "status": "cancelled",
      "items": [
          {
              "id": 1,
              "product": {
                  "id": 1,
                  "name": "Laptop",
                  "description": "High-end laptop",
                  "price": "999.99",
                  "stock": 10,
                  "category": {
                      "id": 1,
                      "name": "Electronics",
                      "description": "Electronic gadgets"
                  },
                  "image": "/media/products/laptop.jpg",
                  "created_at": "2025-06-14T00:00:00Z"
              },
              "quantity": 2,
              "price": "999.99"
          }
      ],
      "shipping_address": "John Doe, 123 Main St, New York",
      "billing_address": "John Doe, 123 Main St, New York",
      "payment_reference": "PAY123",
      "coupon": {
          "id": 1,
          "code": "SALE10",
          "discount_percentage": "10.00",
          "max_discount": null,
          "expiry_date": "2025-12-31T23:59:59Z",
          "is_active": true
      },
      "discount_applied": "199.99",
      "created_at": "2025-06-14T00:00:00Z"
  }
  ```
- **Error Response** (400):
  ```json
  {
      "error": "Cannot cancel order in delivered status"
  }
  ```

## Error Handling

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 200 | Success | `{"id": 1, "name": "Electronics"}` |
| 201 | Resource Created | `{"id": 2, "username": "newuser"}` |
| 400 | Bad Request | `{"error": "Insufficient stock"}` |
| 401 | Unauthorized | `{"detail": "Authentication credentials were not provided."}` |
| 403 | Forbidden | `{"detail": "You do not have permission to perform this action."}` |
| 404 | Not Found | `{"detail": "Not found."}` |

## Throttling

- **Anonymous Users**: 100 requests/day (`anon` scope).
- **Authenticated Users**: 1000 requests/day (`user` scope).
- **Sensitive Endpoints** (`/register/`, `/login/`): 10 requests/hour (`sensitive` scope).
- **Checkout Endpoints** (`/checkout/`, `/checkout/preview/`, `/checkout/validate/`): 50 requests/hour (`checkout` scope).

## Troubleshooting

1. **Registration Errors**:
   - **Issue**: `/api/register/` returns `400 Bad Request` with `username` or `email` errors.
   - **Solution**:
     - Ensure `username` and `email` are unique.
     - Check request body format:
       ```json
       {
           "username": "testuser",
           "email": "test@example.com",
           "password": "Test1234"
       }
       ```
     - Verify server logs for database issues:
       ```bash
       tail -f <project_dir>/logs/django.log
       ```

2. **Authentication Errors**:
   - **Issue**: `401 Unauthorized` on authenticated endpoints.
   - **Solution**:
     - Ensure `Authorization: Bearer <access_token>` header is included.
     - Refresh token if expired:
       ```bash
       curl -X POST -H "Content-Type: application/json" \
         -d '{"refresh": "<refresh_token>"}' \
         http://localhost:8000/api/token/refresh/
       ```

3. **MySQL Connection Issues**:
   - **Issue**: Server fails to start with database errors.
   - **Solution**:
     - Verify MySQL is running: `sudo service mysql status`.
     - Check `settings.py` credentials match MySQL user:
       ```sql
       mysql -u your_mysql_user -p
       SHOW DATABASES;
       ```
     - Ensure `ecommerce_db` exists and migrations are applied:
       ```bash
       python manage.py migrate
       ```

4. **Admin Panel Access**:
   - **Issue**: Cannot access `/admin/`.
   - **Solution**:
     - Create a superuser:
       ```bash
       python manage.py createsuperuser
       ```
     - Log in at `http://localhost:8000/admin/` with superuser credentials.

## Notes
- **Public Endpoints**: `/api/categories/search/`, `/api/products/search/`, `/api/products/filter/`, `/api/register/`, `/api/login/` are accessible without authentication. GET requests to `/api/categories/` and `/api/products/` are also public.
- **Admin Interface**: Only `Category` and `Product` models are registered in `/admin/`. Manage other models (e.g., `User`, `Order`) via API endpoints.
- **Media Files**: Product images are served at `/media/products/<filename>`. Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in `settings.py`.
- **Security**: In production, secure `/admin/` with strong passwords and restrict access (e.g., IP whitelisting). Use HTTPS for API requests.
- **Further Customization**: Extend the API by adding endpoints or registering additional models in `admin.py`.

For issues or questions, contact the API maintainer or check server logs for details.
```
