# Chemical Equipment Analyzer - Desktop Application

A PyQt5-based desktop application that provides the same functionality as the web version, using the Django REST backend.

## Features

- User authentication (login/register)
- CSV file upload and analysis
- Interactive data visualization with Matplotlib
- Equipment statistics dashboard
- Dataset history management
- PDF report generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the Django backend is running on `http://localhost:8000`

3. Run the application:
```bash
python main.py
```

## Requirements

- Python 3.8+
- PyQt5
- Matplotlib
- Requests
- Pandas

## Backend Integration

The application connects to the Django REST API with the following endpoints:
- `/api/auth/login/` - User authentication
- `/api/auth/register/` - User registration
- `/api/upload/` - File upload
- `/api/history/` - Dataset history
- `/api/datasets/{id}/` - Dataset details

## File Structure

- `main.py` - Application entry point
- `auth_window.py` - Authentication interface
- `dashboard_window.py` - Main dashboard with visualizations
- `requirements.txt` - Python dependencies