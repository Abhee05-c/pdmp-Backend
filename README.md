# EstimateRUL – Backend

EstimateRUL Backend is a **FastAPI-based REST API** that powers authentication, role-based access control, organization management, audit logging, and **Remaining Useful Life (RUL)** prediction for industrial engines.

It serves as the core system behind the EstimateRUL platform.

---

## 🚀 Features

### ✅ Authentication & Authorization
- JWT-based authentication
- Secure password hashing (Argon2)
- Role-based access:
  - **USER**
  - **ORG ADMIN**
  - **ADMIN**

### ✅ Organization Management
- Create organizations on signup
- Enable / disable organizations
- Organization-level user management

### ✅ User Management
- Org admins can:
  - Create users
  - List users
  - Disable users
- Admins can:
  - Enable / disable any user
  - View users across organizations

### ✅ RUL Prediction
- Predict Remaining Useful Life using:
  - CSV upload
  - Live sensor data payload
- ML inference handled server-side
- Prediction actions logged for auditing

### 🚧 Live Prediction (Under Development)
- Live streaming-based sensor predictions
- API endpoint structure ready
- Enhancements in progress

### ✅ Audit Logging
- Tracks critical actions:
  - Logins
  - User creation
  - User disable/enable
  - Predictions
- Admin-only access to logs

### ✅ Dashboard APIs
- Organization summary endpoint
- User and prediction statistics

---

## 🛠 Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.13
- **Authentication:** JWT (HS256)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (Render)
- **Password Hashing:** Argon2
- **Deployment:** Render
- **Server:** Uvicorn

---
##📂 Project Structure
api/
├── app.py # Main FastAPI application
├── authJWT.py # JWT creation & password hashing
├── authSchemas.py # Auth request/response schemas
├── payloadSchemas.py # Prediction payload schemas
├── dbmodels.py # SQLAlchemy models
├── database.py # Database connection setup
├── dependencies.py # Auth dependencies
├── auditlog.py # Audit logging logic

-See requirements.txt to install all the dependencies.

---

## 🔐 Environment Variables

Set the following environment variables **before running the server**:

```env
Secret_key=your_jwt_secret_key
database_url=postgresql://user:password@host:port/dbname
```

## Running Locally
- uvicorn api.app:app --reload
## App will be available at : 
- http://localhost:8000
