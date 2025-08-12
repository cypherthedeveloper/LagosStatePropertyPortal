# Lagos State Property Portal API Documentation

## Base URL

```
/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header for protected endpoints:

```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. Authentication & User Management

#### Register a new user

```
POST /auth/register
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "buyer_renter"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "buyer_renter"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Login

```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "buyer_renter"
  }
}
```

#### Get User Profile

```
GET /auth/profile
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "buyer_renter"
}
```

#### Update User Profile

```
PUT /auth/profile
```

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "+2348012345678",
  "avatar": "base64_encoded_image_or_url"
}
```

**Response:**
```json
{
  "message": "Profile updated"
}
```

### 2. Property Management

#### List Properties

```
GET /properties
```

**Query Parameters:**
- `location` - Filter by location
- `price_min` - Minimum price
- `price_max` - Maximum price
- `type` - Property type (residential, commercial, industrial)
- `amenities[]` - Array of amenities

**Response:**
```json
[
  {
    "id": 1,
    "title": "3 Bedroom Apartment in Lekki",
    "price": 25000000,
    "location": "Lekki Phase 1, Lagos",
    "type": "residential",
    "verification_status": "verified",
    "images": ["url1", "url2"]
  },
  {
    "id": 2,
    "title": "Office Space in Victoria Island",
    "price": 50000000,
    "location": "Victoria Island, Lagos",
    "type": "commercial",
    "verification_status": "pending",
    "images": ["url1"]
  }
]
```

#### Get Property Details

```
GET /properties/{id}
```

**Response:**
```json
{
  "id": 1,
  "title": "3 Bedroom Apartment in Lekki",
  "description": "Luxurious 3 bedroom apartment with excellent facilities...",
  "price": 25000000,
  "type": "residential",
  "location": "Lekki Phase 1, Lagos",
  "amenities": ["Swimming Pool", "24/7 Electricity", "Security"],
  "images": ["url1", "url2", "url3"],
  "documents": ["document_url1"],
  "verification_status": "verified",
  "owner": {
    "id": 3,
    "name": "Lagos Real Estate Ltd",
    "role": "real_estate_firm"
  }
}
```

#### Create Property

```
POST /properties
```

**Request Body:**
```json
{
  "title": "3 Bedroom Apartment in Lekki",
  "description": "Luxurious 3 bedroom apartment with excellent facilities...",
  "price": 25000000,
  "type": "residential",
  "location": "Lekki Phase 1, Lagos",
  "amenities": ["Swimming Pool", "24/7 Electricity", "Security"],
  "images": ["base64_encoded_image1", "base64_encoded_image2"],
  "documents": ["base64_encoded_document1"]
}
```

**Response:**
```json
{
  "message": "Property created",
  "id": 1
}
```

#### Update Property

```
PUT /properties/{id}
```

**Request Body:** Same as POST /properties

**Response:**
```json
{
  "message": "Property updated"
}
```

#### Delete Property

```
DELETE /properties/{id}
```

**Response:**
```json
{
  "message": "Property deleted"
}
```

#### Verify Property

```
PATCH /properties/{id}/verify
```

**Request Body:**
```json
{
  "status": "verified"
}
```

**Response:**
```json
{
  "message": "Verification updated"
}
```

### 3. Favorites

#### List Favorites

```
GET /favorites
```

**Response:**
```json
[
  {
    "property_id": 1,
    "title": "3 Bedroom Apartment in Lekki"
  },
  {
    "property_id": 5,
    "title": "2 Bedroom Bungalow in Ajah"
  }
]
```

#### Add to Favorites

```
POST /favorites
```

**Request Body:**
```json
{
  "property_id": 1
}
```

**Response:**
```json
{
  "message": "Added to favorites"
}
```

#### Remove from Favorites

```
DELETE /favorites/{id}
```

**Response:**
```json
{
  "message": "Removed from favorites"
}
```

### 4. Leads & Messaging

#### Create Lead

```
POST /leads
```

**Request Body:**
```json
{
  "property_id": 1,
  "message": "I'm interested in this property. Can I schedule a viewing?"
}
```

**Response:**
```json
{
  "message": "Lead created",
  "lead_id": 1
}
```

#### List Leads

```
GET /leads
```

**Response:**
```json
[
  {
    "id": 1,
    "property": {
      "id": 1,
      "title": "3 Bedroom Apartment in Lekki"
    },
    "buyer": {
      "id": 5,
      "name": "Jane Smith"
    },
    "status": "new",
    "created_at": "2023-11-15T10:30:00Z"
  }
]
```

#### Send Message

```
POST /messages
```

**Request Body:**
```json
{
  "lead_id": 1,
  "message": "Yes, we can arrange a viewing for tomorrow at 2 PM."
}
```

**Response:**
```json
{
  "message": "Sent"
}
```

#### Get Conversation

```
GET /messages/{lead_id}
```

**Response:**
```json
[
  {
    "sender": "buyer",
    "message": "I'm interested in this property. Can I schedule a viewing?",
    "timestamp": "2023-11-15T10:30:00Z"
  },
  {
    "sender": "owner",
    "message": "Yes, we can arrange a viewing for tomorrow at 2 PM.",
    "timestamp": "2023-11-15T11:15:00Z"
  }
]
```

### 5. Payments

#### Initiate Payment

```
POST /payments/initiate
```

**Request Body:**
```json
{
  "property_id": 1,
  "amount": 50000,
  "type": "rent"
}
```

**Response:**
```json
{
  "payment_url": "https://payment-gateway.com/pay/ref123456"
}
```

#### Verify Payment

```
POST /payments/verify
```

**Request Body:**
```json
{
  "transaction_id": "txn_123456789"
}
```

**Response:**
```json
{
  "status": "success",
  "receipt_url": "https://example.com/receipts/123456"
}
```

#### Pay Utility Bills

```
POST /payments/utilities
```

**Request Body:**
```json
{
  "property_id": 1,
  "bill_type": "electricity",
  "amount": 5000
}
```

**Response:**
```json
{
  "payment_url": "https://payment-gateway.com/pay/ref789012"
}
```

#### View Transactions

```
GET /transactions
```

**Response:**
```json
[
  {
    "id": 1,
    "type": "rent",
    "amount": 50000,
    "status": "success",
    "property": {
      "id": 1,
      "title": "3 Bedroom Apartment in Lekki"
    },
    "created_at": "2023-11-10T14:30:00Z"
  },
  {
    "id": 2,
    "type": "electricity",
    "amount": 5000,
    "status": "success",
    "property": {
      "id": 1,
      "title": "3 Bedroom Apartment in Lekki"
    },
    "created_at": "2023-11-12T09:15:00Z"
  }
]
```

### 6. Government & Admin

#### List Unverified Properties

```
GET /compliance/unverified
```

**Response:**
```json
[
  {
    "id": 2,
    "title": "Office Space in Victoria Island",
    "owner": {
      "id": 4,
      "name": "Property Solutions Ltd"
    },
    "created_at": "2023-11-05T16:45:00Z"
  }
]
```

#### Generate Compliance Report

```
GET /compliance/reports
```

**Query Parameters:**
- `start_date` - Report start date (YYYY-MM-DD)
- `end_date` - Report end date (YYYY-MM-DD)

**Response:**
```json
{
  "total_properties": 1000,
  "verified": 800,
  "pending": 150,
  "rejected": 50,
  "by_type": {
    "residential": 600,
    "commercial": 300,
    "industrial": 100
  },
  "by_location": {
    "Lekki": 250,
    "Victoria Island": 200,
    "Ikoyi": 150
  }
}
```

#### List All Users

```
GET /admin/users
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "verified": true
  },
  {
    "id": 2,
    "email": "govt@example.com",
    "name": "Government Agency",
    "role": "government",
    "verified": true
  }
]
```

#### Update User

```
PATCH /admin/users/{id}
```

**Request Body:**
```json
{
  "role": "owner",
  "status": "active"
}
```

**Response:**
```json
{
  "message": "User updated"
}
```

## Data Models

### User
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "buyer_renter",
  "verified": true
}
```

### Property
```json
{
  "id": 1,
  "title": "3 Bedroom Apartment in Lekki",
  "description": "Luxurious 3 bedroom apartment...",
  "price": 25000000,
  "type": "residential",
  "location": "Lekki Phase 1, Lagos",
  "amenities": ["Swimming Pool", "24/7 Electricity", "Security"],
  "images": ["url1", "url2"],
  "documents": ["doc_url1"],
  "verification_status": "verified",
  "owner_id": 3
}
```

### Lead
```json
{
  "id": 1,
  "property_id": 1,
  "buyer_id": 5,
  "status": "new",
  "created_at": "2023-11-15T10:30:00Z"
}
```

### Transaction
```json
{
  "id": 1,
  "type": "rent",
  "amount": 50000,
  "payer_id": 5,
  "payee_id": 3,
  "property_id": 1,
  "status": "success",
  "created_at": "2023-11-10T14:30:00Z"
}
```

## Error Responses

All API errors follow a standard format:

```json
{
  "error": true,
  "message": "Error message description",
  "code": "ERROR_CODE",
  "status": 400
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error