# **Task Manager API (Backend Services)**

A fully REST-based API service for task management with authentication, featuring signup, login, and password reset with OTP email verification.
Built following RESTful design principles with JWT-secured endpoints and consistent error handling.

#### **API is live** -> `api.necromancer.dpdns.org`  you can   test directly with ***curl*** or ***postman***
---

## **Features**

* **Authentication**: Signup, login, forget password  with OTP email verification
* **Task Management**: Full CRUD operations (Add, Update, Retrieve, Delete)
* **Security**:

  * JWT token-based authentication
  * Rate limiting
  * IP banning
  * Fixed-size request memory handling
  * Task Level Security

* **Error Handling**: Consistent and standardized error responses across all endpoints
* **RESTful Design**: Stateless architecture with clean, resource-oriented routes

---

## **Tech Stack**

* **Backend**: Python, Flask, Marshmallow, JWT, Pytest, `uv` (package manager), Alembic
* **Database**: PostgreSQL
* **Containerization**: Docker, Docker Compose
* **Architecture**: Factory Method Pattern for modular and scalable development

---

## **Configuration**

The application supports multiple environments for flexibility:

| Environment    | Description                            | Database            |
| -------------- | -------------------------------------- | ------------------- |
| **DevConfig**  | Default mode for local development     | PostgreSQL (Docker) |
| **ProdConfig** | Optimized configuration for deployment | PostgreSQL          |
| **TestConfig** | Lightweight setup for unit tests       | SQLite (in-memory)  |

---

## **Installation & Usage**

### Using Docker (Recommended)

To spin up the entire stack (Flask + PostgreSQL + Redis):

```bash
docker compose -f docker-compose.prod.yaml up
```

To stop all containers:

```bash
docker compose -f docker-compose.prod.yaml down
```

If you want to **remove all volumes (including the database)**:

```bash
docker compose -f docker-compose.prod.yaml down -v
```

>  **Tip**: Docker setup automatically handles environment variables, DB migrations, and health checks.

---

### Without Docker

If you prefer manual setup:

1. Install and configure **PostgreSQL (>= v17)** and **Redis**.
2. Create and activate a virtual environment:

   ```bash
   uv venv 
   source .venv/bin/activate
   ```
3. Install dependencies:

   ```bash
   uv sync # will sync all dependencies in pyproject.toml (after creating venv)
   ```
4. Run using Gunicorn:

   ```bash
   gunicorn -w 4 -b 127.0.0.1:<port_you_want> app:run
   ```

>**Note:** For smooth experience, Docker is still highly recommended — it handles setup and networking automatically.

---

## **Testing the Endpoints**

Use **Postman** or **curl** to test.(I like CURL)
Each endpoint expects properly structured JSON bodies.
JWT token must be provided in the `Authorization` header for protected routes.

Example header:

```
Authorization: Bearer <your_token_here>
Content-Type: application/json
```
---

### **Example:**

#### 1. singup 

**Request:**

```http
POST /api/auth/signup
```

**Body:**

```json
{
  "username": "Test_user",
  "password": "user#gabbar",
  "email": "user007@gmail.com"
}
```

**Response (201 Created):**

```json
{
  "message":"Test_user user created Sucessfully"
}
```


**Curl Command**
```bash 
 curl -X POST -H "Content-Type: application/json" \
 -H "X-Forwarded-For: 1.2.3.6" \
 -d '{"username" :"miles_10","password" : "miles@123","email":"miles007@gmail.com"}' \
 https://api.necromancer.dpdns.org/api/auth/signup
```


#### 2. login 

**Request:**

```http
POST /api/auth/login
```

**Body:**

```json
{
  "username": "Test_user",
  "password": "user#gabbar",
}
```

**Response (201 Created):**

```json
{
"token":"<token>"
}
```


**Curl Command**
```bash 
 curl -X POST -H "Content-Type: application/json" \
 -H "X-Forwarded-For: 1.2.3.6" \
 -d '{"username" :"miles_10","password" : "miles@123","email":"miles007@gmail.com"}' \
 https://api.necromancer.dpdns.org/api/auth/signup
```


#### 3. Create a Task


**Request:**

```http
POST /api/tasks
```

**Body:**

```json
{
  "title": "Finish backend refactor",
  "description": "Clean  up routes and update Alembic scripts",
  "completion": true
}
```

**Response (201 Created):**

```json
{
  "message": "Task created successfully",
}
```


**Curl Command**
```bash 
curl -X POST -H "Content-Type: application/json" \
-H "X-Forwarded-For: 1.2.3.6" \
-H "Authorization: bearere <token>" \
-d '{"username" :"username_001","password" : "user@gabbar"}' \
https://api.necromancer.dpdns.org/api/tasks/
```

#### 4. Retrieve the task (all created one, it follows the pagination)

**Request:**

```http
GET /api/tasks
```

**Header**:
"Authorization: Bearer <token_given_during_login>"

**Response (201 Created):**

```json
{
"data":[
    {"completion":true,
    "created_at":"2025-10-17T20:46:58Z",
    "description":"Clean  up routes and update Alembic script",
    "due_date":null,
    "id":1,
    "priority":"medium",
    "title":"Finish backend refactor"
    }
    ],
    "meta":{"version":"1.0"},
    "pagination":{
        "has_more":false,
        "limit":10,
        "next_cursor":null,
        "total_returned":1
    }
}
```
**Curl Command**
```bash 
curl -X GET -H "Content-Type: application/json" \
-H "X-Forwarded-For: 1.2.3.6" \
-H "Authorization: bearere <token>" \
https://api.necromancer.dpdns.org/api/tasks/
```

---
---
###  **Incorrect Example**

**Bad Request Body:**

```json
{
  "task_title": "Uknown "
  "description": "Description for the error "
}
```

**Response (400 Bad Request):**

```json
{"errors":
    {
    "code":"BAD_REQUEST",
    "details":{
        "title":["Missing data for required field."],"title_task":["Unknown field."]
    },
    "instance":"/api/tasks#e7c51f5d-513c-4795-9868-6e285beca0da",
    "message":"Invalid input",
    "reason":null,
    "status":400,
    "type":"bad_request"
    }
}
```

---

## **Folder Structure**

```
Task_Manager_API/
├── docker-compose.prod.yaml
├── Dockerfile.prod
├── docker-entrypoint.prod.sh
├── Makefile
├── pyproject.toml
├── run.py
├── README.prod.md
│
├── task_manager_api/            
│   ├── __init__.py
│   ├── config.py                  
│   ├── error_handler.py          
│   ├── logging_config.py          
│   ├── models.py                 
│   ├── schemas.py                 
│   ├── utils.py                  
│   │
│   ├── auth/                      
│   │   ├── routes.py              
│   │   └── __init__.py
│   │
│   ├── tasks/                     
│   │   ├── routes.py
│   │   ├── tasks_utils.py
│   │   └── __init__.py
│   │
│   ├── mail_service/              
│   │   ├── fake_service.py
│   │   ├── real_service.py
│   │   └── __init__.py
│   │
│   ├── middleware/                
│   │   ├── rate_limiter.py
│   │   └── __init__.py
│   │
│   └── templates/                 
│       ├── reset_password.html
│       └── reset_password.txt
│
├── migrations/                    
│   ├── env.py
│   └── versions/
│
├── tests/                         
│   ├── test_auth.py
│   ├── test_task.py
│   └── test_reset_password.py
│
└── uv.lock                       
```

## For interactive and Static Documentaion :
- <a href="https://VAibhav1031.github.io/Task_Manager_API/task_manager_api/templates/static_doc_template/index.html" target="_blank">
    Open static documentation page
  </a>

- For interactive you can go to the live api domain  with **/docs** endpoint at the end like this `api.necromancer.dpdns.org/docs` , you will see swagger based interactive documentation

---
## **Contributions**

Pull requests are welcome!
If you find an issue, please open one under the “Issues” tab describing the bug or enhancement.

