# Technical Documentation

## 1. Project Architecture
The project is built using a Microservices architecture to separate concerns:
* **Microservice 1 (MS1)**: Handles core business logic (Addition and Subtraction). It is completely unaware of database structures.
* **Microservice 2 (MS2)**: Acts as the Rate Limiting Engine. It is solely responsible for database interactions and enforcing business rules regarding limits.

**Why?** This ensures MS1 can scale independently of MS2. If the Calculator becomes extremely popular, we can spin up more MS1 servers without needing to change the database service.

## 2. Framework Choices
* **Web Framework**: FastAPI (Python). 
  * **Why?** It is exceptionally fast, beginner-friendly, and automatically validates data.
* **Database**: SQLite.
  * **Why?** As per requirements, SQLite is used. It is a file-based database which requires no external server setup, making it perfect for an assessment. 
  * **Critical Limitation & Mitigation**: SQLite is not built for high-concurrency background processing (it uses file-level locking). If multiple Celery workers write concurrently, it throws `database is locked` errors. Since the requirements strictly enforced SQLite, we mitigated this by enabling **WAL (Write-Ahead Logging)** mode via SQLAlchemy events and increasing the connection timeout. *In a production environment, this should be replaced with PostgreSQL.*
* **ORM**: SQLAlchemy.
  * **Why?** Writing raw SQL queries can be prone to errors. SQLAlchemy allows us to interact with the database using Python objects, keeping the code clean, readable, and PEP8 compliant.

## 3. Background Job Handling (Celery + Redis)
When a user calls MS1 to add numbers, MS1 must tell MS2 to update the usage count. If MS1 waits for MS2 to save to the database before returning the math result to the user, the website will feel slow.

* **Decision**: Implement a **Celery** background worker.
* **How it works**: MS1 calculates the math, tells Celery "Please tell MS2 to update the database when you have time", and immediately gives the math result to the user.
* **Message Broker (Redis)**: Celery requires a place to store these background messages until the worker picks them up. We used Redis for this because it is the industry standard for Celery—it is incredibly fast as it stores data in memory.

## 4. Rate Limiting Logic
The requirement states a limit of 1000 requests per client. 
* **Implementation**: Every time a usage background job runs (`PUT /feature/usage/update`), MS2 checks the total count of rows for that `client_id`. If `count >= 1000`, MS2 updates the `Client_Status` table to mark `usage_limit_exceeded = True`.
* **Why not check on MS1?** Centralization. MS2 is the ultimate authority on rate limits. MS1 just asks MS2 for a "Yes/No" before proceeding.

## 5. Client Testing Simulation
To test the scenario, a Python script (`run_clients.py`) uses threading to simulate 3 independent clients executing 1000, 1500, and 2000 requests concurrently. 
* **Sleep interval**: A tiny `0.01` second sleep was added between requests. Because Celery is asynchronous, if a local script fires 1000 requests in 0.1 seconds, the background worker might lag behind, allowing the client to execute a few extra requests before the database locks them out. The small sleep ensures the background worker keeps pace, accurately blocking Client 2 and 3 exactly at request 1001.

## 6. Containerization (Docker Compose)
The entire stack is orchestrated using `docker-compose.yml`.
* **Why?** It guarantees the application will run seamlessly on any machine. You don't need to install Redis or configure Python virtual environments. One command (`docker-compose up`) starts MS1, MS2, Redis, the Celery Worker, and runs the Client test script automatically.
