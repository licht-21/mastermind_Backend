# Mastermind - Quick Reference Guide
## For Presentations

---

## 🎯 What is Mastermind?

A **Flask REST API** for tracking savings goals. Users can:
- Create multiple savings goals (e.g., "Vacation $5000", "Car $25000")
- Add deposits to goals (track progress)
- View transaction history
- Archive completed goals
- Customize settings (dark mode, date format)

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                  Mobile App (Android)                        │
│              Makes HTTP Requests to API                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                HTTP (Port 5000)
                         │
        ┌────────────────▼────────────────┐
        │   Flask Web Server (run.py)     │
        │   - Routes incoming requests    │
        │   - Validates input             │
        │   - Calls business logic        │
        └────────────────┬────────────────┘
                         │
              ┌──────────▼──────────┐
              │  app/routes.py      │
              │  (API Endpoints)    │
              └──────────┬──────────┘
                         │
        ┌────────────────▼────────────────┐
        │  MySQL Database (saving_db)     │
        │  ┌──────────────────────────┐  │
        │  │ - users                  │  │
        │  │ - savings_goals          │  │
        │  │ - deposits               │  │
        │  │ - user_settings          │  │
        │  └──────────────────────────┘  │
        └─────────────────────────────────┘
```

---

## 📊 Database Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | User accounts | id, name, email, password |
| **savings_goals** | Goals to track | id, user_id, name, target_amount, current_amount, due_date, is_archived |
| **deposits** | Money added | id, goal_id, amount, note, created_at |
| **user_settings** | Preferences | user_id, dark_mode, date_format |

---

## 🔧 How to Run (3 Steps)

### 1. Setup
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mysql -u root -p < schema.sql
```

### 2. Configure
Edit `config.py` with your MySQL credentials

### 3. Run
```bash
python run.py
```
Server starts at `http://0.0.0.0:5000`

---

## 📡 Main API Endpoints

### User Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/register` | Create new account |
| POST | `/api/login` | Login and get user ID |

### Savings Goals (require X-User-Id header)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/savings` | List all goals (with sort/filter) |
| POST | `/api/savings` | Create new goal |
| PUT | `/api/savings/<id>` | Update goal |
| DELETE | `/api/savings/<id>` | Delete goal |
| POST | `/api/savings/<id>/deposit` | Add money to goal |
| POST | `/api/savings/<id>/archive` | Archive completed goal |
| POST | `/api/savings/<id>/duplicate` | Copy goal for next period |
| GET | `/api/savings/<id>/deposits` | View transaction history |

### Summary & Settings
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/savings/summary` | Get totals & stats |
| GET | `/api/settings` | Get user preferences |
| PUT | `/api/settings` | Update preferences |

---

## 💾 Example API Flow

### 1. User Registers
```
Request:  POST /api/register
Body:     {"username": "john", "email": "john@mail.com", "password": "pass123"}
Response: 201 Created → user_id: 1
```

### 2. User Creates Goal
```
Request:  POST /api/savings
Headers:  X-User-Id: 1
Body:     {"name": "Vacation", "targetAmount": 5000, "currentAmount": 0, "dueDate": "2026-12-31"}
Response: 201 Created → goal_id: 1, progressPercent: 0
```

### 3. User Deposits Money
```
Request:  POST /api/savings/1/deposit
Headers:  X-User-Id: 1
Body:     {"amount": 500, "note": "First deposit"}
Response: 200 OK → progressPercent: 10
```

### 4. User Views Progress
```
Request:  GET /api/savings?sort=progress
Headers:  X-User-Id: 1
Response: 200 OK → [goal with updated amount and progress]
```

---

## 🔑 Key Features Explained

### ✅ Auto-Archiving
- Goal automatically archives when: `currentAmount >= targetAmount`
- Archived goals don't accept deposits
- Can manually archive anytime

### ✅ Overdue Detection
- Goal is overdue if: `dueDate < TODAY` AND `currentAmount < targetAmount` AND `not archived`
- Displayed in goal details and summary

### ✅ Progress Calculation
```
progressPercent = (currentAmount / targetAmount) * 100
// Capped at 100%
```

### ✅ Transaction History
- Every deposit creates a record in `deposits` table
- Shows: amount, date, optional note
- Helps users track spending patterns

### ✅ Security
- User ID validated from header (X-User-Id)
- SQL injection prevented via parameterized queries
- Users can only see their own goals

---

## 📈 Request/Response Pattern

All API responses follow this format:

**Success (2xx):**
```json
{
  "status": "success",
  "data": { /* goal, user, etc */ }
}
// OR just the data directly for GET requests
```

**Error (4xx/5xx):**
```json
{
  "status": "error",
  "message": "Description of what went wrong"
}
```

---

## 🎬 Request Flow (Simplified)

```
1. Request comes in (e.g., POST /api/savings)
   ↓
2. Flask matches to route function (e.g., create_savings_goal)
   ↓
3. Extract & validate data
   ↓
4. Connect to MySQL database
   ↓
5. Execute SQL query
   ↓
6. Format response JSON
   ↓
7. Close database connection
   ↓
8. Send HTTP response back to client
```

---

## 🚨 Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | Goal updated successfully |
| **201** | Created | New goal created |
| **400** | Bad Request | Missing required field |
| **401** | Unauthorized | Missing X-User-Id header |
| **404** | Not Found | Goal ID doesn't exist |
| **500** | Server Error | Database connection failed |

---

## 🔐 Security Features

✅ **Parameterized Queries** - Prevents SQL injection  
✅ **User ID Validation** - Only users see their own data  
✅ **Input Validation** - Checks data types and ranges  
✅ **Foreign Keys** - Ensures data consistency  
✅ **Cascade Deletes** - Automatic cleanup when user deleted  

---

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `run.py` | Entry point - starts the Flask server |
| `config.py` | Database credentials |
| `app/__init__.py` | Flask app setup & initialization |
| `app/routes.py` | All API endpoint logic (~600 lines) |
| `schema.sql` | Database structure & tables |
| `requirements.txt` | Python dependencies |

---

## ⚡ Performance Considerations

- **Indexes** on user_id and archived status for fast queries
- **Connection pooling** could be added for production
- **Gunicorn** recommended for production (handles concurrency)
- **MySQL credentials** should use environment variables (not hardcoded)

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Flask framework basics
- ✅ REST API design principles
- ✅ MySQL database interaction
- ✅ Request/response handling
- ✅ Input validation & error handling
- ✅ SQL parameterized queries
- ✅ Authentication via headers
- ✅ Data relationships & integrity

---

## 💡 Possible Enhancements

1. **Password Hashing** - Use bcrypt instead of plain text
2. **JWT Tokens** - Replace X-User-Id header
3. **Rate Limiting** - Prevent API abuse
4. **Pagination** - For large goal lists
5. **Search** - Find goals by name
6. **Categories** - Group goals by type
7. **Recurring Goals** - Auto-reset monthly
8. **Email Notifications** - Alerts for overdue goals
9. **Data Export** - CSV/PDF reports
10. **Mobile App** - Android/iOS client

---

**For full details, see: DOCUMENTATION.md**
