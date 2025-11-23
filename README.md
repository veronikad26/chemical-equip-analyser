# Chemical Equipment Analyser  
## Complete Setup & Installation Guide

This README provides all necessary instructions to set up and run both the **Web Version** (React + Django) and the **Desktop Version** (PyQt5 + Django) of the Chemical Equipment Analyser.

---


## 1.1 Prerequisites  
- Python 3.8 or higher  
- pip  
- Node.js (version 16 or higher recommended)
- pip (Python package installer)

---

## 1.2 Backend Setup (Django)

### Step 1 — Navigate to the backend directory
cd backend 

### Step2- Install Backend requirements 
pip install -r requirements.txt

### Step 3 — Run database migrations
python manage.py migrate

### Step 4- Start the Django development server
python manage.py runserver

The backend will now run on:
http://127.0.0.1:8000


## 1.3 Frontend Setup- Web version (React)

### Step 1 — Navigate to the frontend directory
cd frontend 

### Step 2 — Install Node.js dependencies
npm install

### Step 3 — Start the React development server
npm start

The frontend will now run on:
http://localhost:3000


## 1.4 Frontend Setup- Desktop version (PyQt5)

### Step 1- Navigate to the desktop frontend directory
cd desktop-frontend

### Step 2- Install desktop dependencies
pip install -r requirements.txt

### Step 3- Run the desktop application
python main.py