# Quick Start Guide

## Prerequisites

- Python 3.7 or higher
- Node.js 14 or higher
- npm 6 or higher

## Installation

1. **Install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   # Windows
   setup_backend.bat
   
   # Unix/Linux/Mac
   chmod +x setup_backend.sh
   ./setup_backend.sh
   ```

## Running the Application

### Option 1: Using npm scripts

1. **Start the frontend:**
   ```bash
   npm run dev
   ```

2. **Start the backend (in a separate terminal):**
   ```bash
   npm run backend:dev
   ```

### Option 2: Using batch scripts (Windows)

1. **Start the frontend:**
   ```bash
   npm run dev
   ```

2. **Start the backend:**
   ```bash
   start_backend.bat
   ```

### Option 3: Using shell scripts (Unix/Linux/Mac)

1. **Start the frontend:**
   ```bash
   npm run dev
   ```

2. **Start the backend:**
   ```bash
   chmod +x start_backend.sh
   ./start_backend.sh
   ```

### Option 4: Using Docker

1. **Build and start both services:**
   ```bash
   docker-compose up --build
   ```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs (when implemented)

## Testing the API

You can test the API endpoints using the example client:

```bash
cd backend
python example_client.py
```

## Next Steps

1. Configure Firebase credentials for Firestore access
2. Customize the data processing pipelines
3. Train and deploy machine learning models
4. Extend the API with additional endpoints