# API Documentation

## Microservice 1 (Calculator)

### 1. Add Numbers
- **Endpoint**: `/add`
- **Method**: `POST`
- **Description**: Adds two numbers together. Checks with the Rate Limiter if the client is allowed. Updates usage in the background.
- **Request Body** (JSON):
  ```json
  {
    "client_id": "string",
    "num1": 10.5,
    "num2": 5.0
  }
  ```
- **Responses**:
  - `200 OK`: `{"result": 15.5}`
  - `403 Forbidden`: `{"detail": "Usage limit exceeded..."}`

### 2. Subtract Numbers
- **Endpoint**: `/subtract`
- **Method**: `POST`
- **Description**: Subtracts num2 from num1. Checks with the Rate Limiter if the client is allowed. Updates usage in the background.
- **Request Body** (JSON):
  ```json
  {
    "client_id": "string",
    "num1": 10.5,
    "num2": 5.0
  }
  ```
- **Responses**:
  - `200 OK`: `{"result": 5.5}`
  - `403 Forbidden`: `{"detail": "Usage limit exceeded..."}`

---

## Microservice 2 (Rate Limiter Engine)

### 1. Update Feature Usage
- **Endpoint**: `/feature/usage/update`
- **Method**: `PUT`
- **Description**: Records that a client performed an operation. If they reach 1000 requests, they are blocked.
- **Request Body** (JSON):
  ```json
  {
    "client_id": "string",
    "operation_name": "string"
  }
  ```
- **Responses**:
  - `200 OK`: `{"message": "Usage updated successfully", "current_count": 50}`

### 2. Update Client Status
- **Endpoint**: `/status/update/`
- **Method**: `POST`
- **Description**: Manually updates whether a client is blocked from using the service (useful for admins).
- **Request Body** (JSON):
  ```json
  {
    "client_id": "string",
    "usage_limit_exceeded": true
  }
  ```
- **Responses**:
  - `200 OK`: `{"message": "Status updated successfully"}`

### 3. Get Client Status
- **Endpoint**: `/status/get`
- **Method**: `GET`
- **Description**: Returns whether a client is currently blocked (limit exceeded) or allowed.
- **Query Parameters**:
  - `client_id` (string): The ID of the client.
- **Responses**:
  - `200 OK`: `{"client_id": "string", "usage_limit_exceeded": false}`
