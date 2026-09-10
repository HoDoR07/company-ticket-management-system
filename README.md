# company-ticket-management-system
A full-stack company ticket management system for creating, assigning, tracking, and resolving support tickets.


# Company Ticket Management System

A full-stack company ticket management system for creating, assigning, tracking, and resolving support tickets based on user roles.

## Features

### Employee

* Register and login
* View and update profile
* Create support tickets
* View own tickets
* Update and delete own tickets
* Track ticket status and assignment

### Technician

* View assigned tickets
* Update ticket status
* Move tickets to `In Progress` or `Resolved`

### Admin

* View and manage users
* Update user roles
* View all tickets
* Assign tickets to technicians
* Update ticket priority and status
* Filter tickets by status and priority
* Delete tickets
* View dashboard statistics

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* JWT Authentication
* Redis
* HTML
* CSS
* JavaScript
* Alembic
* Postman

## Architecture

```text
Frontend
HTML + CSS + JavaScript
        ↓
FastAPI REST API
        ↓
SQLAlchemy
        ↓
PostgreSQL

FastAPI
   ↓
Redis
(Caching)
```

## Authentication & Authorization

The application uses JWT-based authentication with role-based authorization.

Supported roles:

* Employee
* Technician
* Admin

Each role has access only to the operations permitted for that role.

## Caching

Redis is used for caching frequently accessed ticket data.

Cache entries are invalidated when relevant ticket data is created, updated, deleted, assigned, or modified.

## Database Migrations

Alembic is used to manage database schema migrations.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/HoDoR07/company-ticket-management-system.git
cd company-ticket-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add the required database, Redis, and JWT configuration.

> Never commit your `.env` file to GitHub.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Project Structure

```text
company-ticket-management-system/
│
├── alembic/
├── app/
│   ├── routers/
│   │   ├── admin.py
│   │   ├── technician.py
│   │   ├── tickets.py
│   │   └── users.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── oath2.py
│   ├── redis.py
│   ├── schemas.py
│   └── utils.py
│
├── frontend/
│   ├── admin.html
│   ├── employee.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── technician.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
├── alembic.ini
└── requirements.txt
```

## Project Highlights

* Role-based access control
* JWT authentication
* RESTful API design
* PostgreSQL database integration
* Redis caching
* Database migrations with Alembic
* Separate dashboards for Employee, Technician, and Admin
* Frontend integrated with FastAPI
* API testing with Postman
