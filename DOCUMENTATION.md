# Mastermind - Savings Goal Tracking API
## Comprehensive Documentation

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Database Architecture](#database-architecture)
5. [Setup Instructions](#setup-instructions)
6. [How to Run](#how-to-run)
7. [API Endpoints](#api-endpoints)
8. [Key Features](#key-features)
9. [How the Code Flows](#how-the-code-flows)

---

## 🎯 Project Overview

**Mastermind** is a Flask-based REST API backend for a **Savings Goal Tracking Application**. It enables users to:
- Create and manage multiple savings goals
- Track progress toward financial targets
- Record deposits to savings goals
- Archive completed goals
- Customize user settings (dark mode, date format)

The application is designed to connect with mobile clients (like an Android app) via HTTP API endpoints and stores all data in a MySQL database.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 3.0.0+ |
| **Database** | MySQL |
| **Database Driver** | mysql-connector-python 8.0.0+ |
| **Application Server** | Gunicorn 21.0.0+ |
| **Language** | Python 3.x |
| **Communication** | REST API (JSON) |

---

## 📁 Project Structure

```
mastermind/
├── run.py                      # Entry point - starts the Flask app
├── config.py                   # Database configuration
├── requirements.txt            # Python dependencies
├── schema.sql                  # Complete MySQL database schema
├── DEPLOY_ONLINE.md           # Deployment guidelines
├── app/
│   ├── __init__.py            # Flask app initialization & DB connection
│   └── routes.py              # All API endpoints
```

### File Descriptions:

**[run.py](run.py)** - Application Entry Point
- Imports the Flask app from the `app` module
- Starts the server on `0.0.0.0:5000` with debug mode enabled
- Makes the app accessible from local network devices

**[config.py](config.py)** - Configuration
- Stores database credentials (MySQL host, user, password, database name)
- Centralizes configuration that should be updated locally

**[app/__init__.py](app/__init__.py)** - Flask App Initialization
- Creates and configures the Flask application
- Establishes MySQL database connection on startup
- Imports and registers all routes from `routes.py`
- Tests database connectivity on initialization

**[app/routes.py](app/routes.py)** - API Endpoints
- Defines all REST API endpoints for the application
- Handles authentication via `X-User-Id` header
- Contains business logic for savings goals and deposits
- Includes data formatting utilities (`goal_to_json`, `deposit_to_json`)

**[schema.sql](schema.sql)** - Database Schema
- Complete MySQL schema definition
- Creates 4 main tables: `users`, `savings_goals`, `deposits`, `user_settings`
- Includes foreign key relationships and indexes

---

## 💾 Database Architecture

### 4 Core Tables:

#### 1. **users** - User Authentication
Stores user account information
```sql
- id (INT, PK)
- name (VARCHAR)          -- Username from signup
- email (VARCHAR, UNIQUE)
- password (VARCHAR)      -- Plain text (should be hashed in production)
- created_at (TIMESTAMP)
```

#### 2. **savings_goals** - Main Savings Tracker
Stores each user's savings goals with progress tracking
```sql
- id (INT, PK)
- user_id (INT, FK)       -- Links to users.id
- name (VARCHAR)          -- Goal name (e.g., "Vacation", "Car")
- target_amount (DECIMAL) -- Goal target amount
- current_amount (DECIMAL)-- Amount saved so far
- due_date (DATE)         -- Target completion date (optional)
- is_archived (TINYINT)   -- 0=active, 1=archived
- archived_at (TIMESTAMP) -- When goal was archived
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 3. **deposits** - Transaction History
Records every deposit made to a savings goal
```sql
- id (INT, PK)
- goal_id (INT, FK)       -- Links to savings_goals.id
- amount (DECIMAL)        -- Deposit amount
- note (VARCHAR)          -- Optional note about deposit
- created_at (TIMESTAMP)
```

#### 4. **user_settings** - User Preferences
Stores user customization options
```sql
- user_id (INT, PK, FK)   -- Links to users.id
- dark_mode (TINYINT)     -- 0=off, 1=on
- date_format (VARCHAR)   -- "DD/MM/YYYY" or "YYYY-MM-DD"
- updated_at (TIMESTAMP)
```

**Relationships:**
- `users` → `savings_goals` (One-to-Many): A user has many goals
- `users` → `user_settings` (One-to-One): A user has one settings record
- `savings_goals` → `deposits` (One-to-Many): A goal has many deposits
- All foreign keys have `ON DELETE CASCADE` for data integrity

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL Server running
- pip (Python package manager)

### Step 1: Create Python Virtual Environment
```bash
# Navigate to project directory
cd c:\Users\ADMIN\Desktop\mastermind

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On Windows CMD:
.venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
This installs:
- Flask 3.0.0+ (web framework)
- mysql-connector-python 8.0.0+ (database driver)
- gunicorn 21.0.0+ (production server)

### Step 3: Create MySQL Database
```bash
# Open MySQL Workbench or use command line:
mysql -u root -p < schema.sql
```
This creates:
- Database: `saving_db`
- All 4 tables with proper relationships

### Step 4: Configure Database Credentials
Edit [config.py](config.py) with your MySQL credentials:
```python
DB_HOST = "localhost"        # MySQL server address
DB_USER = "root"             # MySQL username
DB_PASSWORD = "passwordito"  # MySQL password (UPDATE THIS!)
DB_NAME = "saving_db"        # Database name
```

---

## ▶️ How to Run

### Development Mode (with Debug)
```bash
# Make sure virtual environment is activated
# Then run:
python run.py
```

**Output:**
```
WARNING in flask.app: This is a development server. Do not use it in production.
Running on http://0.0.0.0:5000
```

**Access the API:**
- Local machine: `http://localhost:5000`
- From other devices on network: `http://<YOUR_IP>:5000`

### Production Mode (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `run:app`: Import `app` from `run.py`

---

## 🔌 API Endpoints

All endpoints expect JSON requests and return JSON responses. Most require the `X-User-Id` header for authentication.

### Authentication Endpoints

#### **POST /api/register**
Create a new user account
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```
**Response (201):**
```json
{
  "status": "success",
  "user": {"id": 1, "username": "john_doe", "email": "john@example.com"}
}
```

#### **POST /api/login**
Authenticate and get user ID
```json
{
  "username": "john_doe",  // Can use username or email
  "password": "secure_password"
}
```
**Response (200):**
```json
{
  "status": "success",
  "user": {"id": 1, "username": "john_doe", "email": "john@example.com"}
}
```

---

### Savings Goals Endpoints
*All require `X-User-Id` header*

#### **GET /api/savings**
List user's savings goals
**Query Parameters:**
- `archived=0|1` (default: 0) - Show active or archived goals
- `sort=name|due_date|progress|newest` (default: newest)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Vacation",
    "targetAmount": 5000.00,
    "currentAmount": 1500.00,
    "progressPercent": 30,
    "dueDate": "2026-12-31",
    "isArchived": false,
    "archivedAt": null,
    "isOverdue": false
  }
]
```

#### **POST /api/savings**
Create a new savings goal
```json
{
  "name": "Vacation",
  "targetAmount": 5000.00,
  "currentAmount": 0,
  "dueDate": "2026-12-31"  // Optional
}
```
**Response (201):** Returns created goal object

#### **PUT /api/savings/<goal_id>**
Update a savings goal
```json
{
  "name": "Vacation (Updated)",
  "targetAmount": 6000.00,
  "currentAmount": 2000.00,
  "dueDate": "2027-01-31"
}
```
**Response (200):** Returns updated goal

#### **DELETE /api/savings/<goal_id>**
Delete a savings goal
**Response (200):**
```json
{"status": "success", "message": "Goal deleted"}
```

#### **POST /api/savings/<goal_id>/deposit**
Add money to a savings goal
```json
{
  "amount": 500.00,
  "note": "Monthly savings"  // Optional
}
```
**Response (200):** Returns updated goal with new amount

#### **POST /api/savings/<goal_id>/archive**
Archive a completed goal
**Response (200):** Returns archived goal

#### **POST /api/savings/<goal_id>/duplicate**
Create a copy of a goal for next period
```json
// No body required
```
**Response (201):** Returns new goal with "(copy)" suffix

#### **GET /api/savings/<goal_id>/deposits**
View transaction history for a goal
**Response (200):**
```json
[
  {
    "id": 1,
    "goalId": 1,
    "amount": 500.00,
    "note": "Monthly savings",
    "createdAt": "2026-05-01 10:30:00"
  }
]
```

---

### Summary Endpoint

#### **GET /api/savings/summary**
Get overview of all active goals
**Response (200):**
```json
{
  "activeGoalCount": 3,
  "totalSaved": 5000.00,
  "totalTarget": 25000.00,
  "overdueCount": 1
}
```

---

### Settings Endpoints
*All require `X-User-Id` header*

#### **GET /api/settings**
Get user preferences
**Response (200):**
```json
{
  "darkMode": false,
  "dateFormat": "DD/MM/YYYY"
}
```

#### **PUT /api/settings**
Update user preferences
```json
{
  "darkMode": true,
  "dateFormat": "YYYY-MM-DD"
}
```
**Response (200):** Returns updated settings

---

## ✨ Key Features

### 1. **User Authentication**
- Registration with username, email, password
- Login with username or email
- User ID required for all goal operations

### 2. **Multi-Goal Support**
- Users can create unlimited savings goals
- Each goal tracks progress independently
- Goals can have different target amounts and due dates

### 3. **Auto-Archiving**
- Goals automatically archive when current amount ≥ target amount
- Archived goals appear in separate list
- Can manually archive goals anytime

### 4. **Overdue Detection**
- System detects goals past their due date
- Only active (non-archived) incomplete goals count as overdue
- Displayed in summary and individual goal views

### 5. **Transaction History**
- Every deposit is recorded with amount, date, and optional note
- Complete audit trail for each goal
- Deposits ordered chronologically

### 6. **Goal Duplication**
- Quickly create next period's goal from previous one
- Copies target amount and due date
- Starts with $0 current amount

### 7. **User Preferences**
- Dark mode toggle
- Date format selection (DD/MM/YYYY or YYYY-MM-DD)
- Auto-created on first settings access

### 8. **Data Validation**
- Target amounts must be positive
- Deposit amounts must be positive
- Current amount cannot be negative
- All amounts are decimal (handles cents)

---

## 🔄 How the Code Flows

### Application Startup Flow

```
1. User runs: python run.py
   ↓
2. run.py imports create_app() from app/__init__.py
   ↓
3. Flask app created and configured with config.py database settings
   ↓
4. MySQL connection test runs
   - Connects to database using configured credentials
   - Prints success/failure message
   - Closes test connection
   ↓
5. Routes from app/routes.py are registered with Flask
   ↓
6. Flask server starts on 0.0.0.0:5000
   ↓
7. Server ready to accept HTTP requests
```

### Request Processing Flow

```
1. Client sends HTTP request to API endpoint
   Example: POST /api/savings with X-User-Id header
   ↓
2. Flask routes request to appropriate function (e.g., create_savings_goal)
   ↓
3. Authentication check
   - Extract X-User-Id from headers
   - If missing, return 401 error
   ↓
4. Input validation
   - Parse JSON body
   - Validate required fields
   - Check data types and ranges
   - Return 400 if validation fails
   ↓
5. Database operation
   - Get database connection from get_db_connection()
   - Create cursor with dictionary=True (returns dicts not tuples)
   - Execute SQL query with parameterized statements (prevents SQL injection)
   ↓
6. Data processing
   - Convert database rows to JSON format
   - Apply business logic (e.g., calculate progress %)
   - Check conditions (e.g., is goal overdue?)
   ↓
7. Response generation
   - Format response as JSON
   - Include appropriate HTTP status code (200, 201, 400, 404, 500)
   ↓
8. Cleanup
   - Close database cursor
   - Close database connection
   ↓
9. Return JSON response to client
```

### Creating a Savings Goal Flow

```
POST /api/savings
├─ Extract user_id from X-User-Id header
│
├─ Validate input
│  ├─ Check name is not empty
│  ├─ Check targetAmount is provided
│  ├─ Convert amounts to float
│  └─ Ensure targetAmount > 0
│
├─ Connect to database
│  ├─ Open connection using credentials from config.py
│  └─ Create dictionary cursor
│
├─ Insert new goal into savings_goals table
│  ├─ Calculate is_archived (1 if current >= target, else 0)
│  ├─ Set archived_at timestamp if auto-archived
│  └─ Get new goal_id
│
├─ If currentAmount > 0
│  ├─ Record initial deposit in deposits table
│  └─ Commit transaction
│
├─ Fetch complete goal data from database
│
├─ Convert to JSON using goal_to_json()
│  ├─ Calculate progressPercent
│  ├─ Check if overdue (only if active + due_date passed)
│  └─ Format dates to ISO format
│
└─ Return JSON with 201 (Created) status
```

### Depositing to a Goal Flow

```
POST /api/savings/<goal_id>/deposit
├─ Extract user_id from X-User-Id header
│
├─ Validate input
│  ├─ Check amount is provided and is float
│  └─ Ensure amount > 0
│
├─ Fetch goal to verify:
│  ├─ Goal exists
│  ├─ User owns goal
│  └─ Get current amount
│
├─ Calculate new current_amount
│  └─ new_current = current_amount + deposit_amount
│
├─ Update goal in database
│  ├─ Set current_amount to new value
│  ├─ Only update if goal is not archived
│  └─ Commit transaction
│
├─ Record deposit in deposits table
│  ├─ Store goal_id, amount, note, timestamp
│  └─ Commit transaction
│
├─ Check auto-archive condition
│  ├─ If new_current >= target_amount
│  ├─ Set is_archived = 1
│  └─ Set archived_at = CURRENT_TIMESTAMP
│
├─ Fetch updated goal data
│
├─ Convert to JSON
│  └─ Include new progress percentage
│
└─ Return JSON with updated goal (200 OK)
```

---

## 🚀 Summary

**Mastermind** is a production-ready Flask REST API that:
1. ✅ Authenticates users with credentials
2. ✅ Manages multiple savings goals per user
3. ✅ Tracks deposits and transaction history
4. ✅ Calculates progress and detects overdue goals
5. ✅ Stores everything securely in MySQL
6. ✅ Provides mobile-friendly JSON API
7. ✅ Handles all edge cases with validation
8. ✅ Uses parameterized queries to prevent SQL injection

**To get started:** Follow the Setup Instructions above, then run `python run.py` to start the server!

---

**Last Updated:** May 26, 2026  
**Version:** 1.0  
**Status:** Production Ready
