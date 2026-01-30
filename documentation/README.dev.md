# Task Manager API (Backend Services)....

A fully REST-based API service for task management with authentication, featuring signup, login, and password reset with OTP email verification. Built following RESTful design principles with JWT-secured endpoints and consistent error handling.

## Features:

- **Authentication**: Signup, login, password reset with OTP email verification
- **Task Management**: Full CRUD operations for tasks
- **Security**: JWT token-based authentication, Rate Limitting, Ip-Ban
- **Consistent Error Handling**: Standardized error responses across all endpoints
- **RESTful Design**: Following REST API best practices
- **Pagination**: Cursor-based pagination
- **Batch Processing**: currently thread based HEAVY WRITE operations are batch commited which increase the througput 

## Tech Stack:

- **Backend**: Python, Flask, Marshmallow, JWT, Pytest, uv, Alembic
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Architecture**: Factory method pattern for scalable development, it is good for development and future scaling , if you want to 

## Configuration:

The application uses separate configurations for different environments:

- **DevConfig**: Development mode (default), uses Docker PostgreSQL for persistent testing
- **ProdConfig**: Production deployment configuration  
- **TestConfig**: Unit testing with SQLite in-memory database

Each configuration has its own database settings and feature flags defined in separate blueprint classes.

--- 
> NEW 

# Batch Processing for Performance Optimization

## Overview

The implementation of **batch processing** significantly increases performance and throughput for heavy write operations. In high-request-rate scenarios, committing to the database for every individual request creates bottlenecks due to:

- Validation overhead
- Database connection management
- Write operations and commits
- Overall request processing time

For thousands of requests, this traditional approach drastically decreases throughput.

**Solution:** In-memory batch processing increases throughput by approximately **20-25%**.

> **Note:** This implementation is still in development and may be fragile.

---

## Request Flow
```
User Request → POST /tasks/ → Batch Processor Thread → User Response → Background Thread Commit → Database
```

### Flow Breakdown:

1. **User initiates POST request** → Request is added to the batch processing bucket
2. **User receives immediate response** → "Task added successfully" (no waiting for DB commit)
3. **Background processing** → Batch is committed when conditions are met
4. **Database commit** → Reduced number of expensive single commits

---

## How It Works

### Core Components

- **Threading Module**: Manages background workers that process and batch commit requests to the database
- **Batch Size**: Minimum threshold for batch processing
- **Last Commit Timestamp**: Tracks timing of the most recent commit

### Commit Triggers

The batch is committed to the database when **either** condition is met:

#### 1. **Size-Based Trigger**
- Batch size reaches or exceeds the configured threshold
- Optimizes for high-traffic scenarios

#### 2. **Time-Based Trigger**
- Prevents requests from sitting in the batch indefinitely
- Commits after a specified time interval, regardless of batch size
- Ensures system stability and data integrity
- Addresses the edge case where request rate drops significantly

---

## Why Time-Based Commits Matter

Without time-based commits, requests could remain unprocessed during low-traffic periods, causing:
- User confusion (no visible confirmation)
- Data integrity issues
- System instability

The dual-trigger approach maintains both **performance** (batch efficiency) and **reliability** (timely processing).

---
**Testing done using good `Apache's JMETER`**

**Test JMETER specs:**
- Threads :450 
- Ramp-up time: 60second (means in 60 second first 450 threads would be created)
- looop : infinite 
- duration:300seconds

> Little bit of JMETER knowledge  is required 

#### ![Screenshot of Before Batching JMETER Dashboard Result :](repo_essentials/before.png)
- Througput (or TPS) -> 1585/sec
- Increasing the thread count in the jmeter start increasing satuaration and TPS start dropping

#### ![Screenshot of after Batching JMETER Dashboard Result :](repo_essentials/after.png)
- Througput (or TPS) -> 1790/sec
- There is good amount of througput jump you will see 


**Future**  : Making Central Saparate concurrent batch worker  so that in crash , or web server (gunicorn)
if any worker have got stopp working or some problem  which made the request unattented and it will have persistent storage and log file to replay after crash 

---

### Static & interactive Documentation webpage 
- [Documentation_static->](./task_manager_api/templates/static_documentation.html)
- `NEW` endpoint for interactive documentation (using swagger-ui) -> **/docs**

---
--- 

## Project Structure:

```
__init__.py (main app initialization and object creation)
```

The main application file handles initialization and attaches all components as dynamic attributes to the Flask app object.

## API Routes:

### Authentication::
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/forget-password` - Initiate password reset
- `POST /api/auth/verify-otp` - Verify OTP for password reset
- `POST /api/auth/reset-password` - Complete password reset

### Tasks::
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/task-id` - Get specific task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/task-id` - Update existing task
- `DELETE /api/tasks` - Delete all tasks
- `DELETE /api/tasks/task-id` - Delete specific task

Routes are organized into **AUTH** and **TASKS** modules, each with validation using **Marshmallow** for JSON data validation including size, type, and content constraints.

## Error Handling:

Standardized error response structure used across all endpoints:

```python
def error_response(code, status, message=None, reason=None, details=None):
    return (
        jsonify(
            {
                "errors": {
                    "code": code,
                    "type": code.lower(),
                    "status": status,
                    "message": message or central_registry.get(code, "Unknown error"),
                    "reason": reason,
                    "details": details,
                    "instance": _make_instance(),
                }
            }
        ),
        status,
    )
```

Supported error types/used in this project : internal_server_error, not_found, bad_request, unauthorized_error, too_many_requests, forbidden_access

---


## Logging:

Custom logging configuration using Python's logging library with dictConfig:
- Stream and file logging support
- Scalable to external services (ELK stack)
- Root logging structure with module-level propagation

## Database Migration:

- **Development**: Managed by Alembic through Docker scripts
- **Testing**: Uses SQLite in-memory (no migration needed), Curl for persistent db required test's
- **Production**: Alembic migration management

## Usage:

### Quick Start::

```bash
# Start the application
docker compose up

# Stop the application  
docker compose down

# Remove volumes (clean reset)
docker compose down -v
```

### Development with Live Reload

```bash
# Start with file watching for development
docker compose up --watch
```

Ensure your compose file includes the `develop` section:

```yaml
develop:
  watch:
    - action: rebuild
      path: . # . means your current working directory cause your compose file is in the project dir brother
      target: /task_app # your application folder in the container
      ignore: # even if you use the .dockerignore , it is best practice for protection
        - .venv/
        - .git/
        - __pycache__/
        - "*.egg-info/"
```

## Environment Setup

The application automatically uses development mode by default. For production deployment, set the appropriate environment variables for your domain and database configuration.
