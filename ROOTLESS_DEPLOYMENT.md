# Rootless Deployment Guide

This guide explains how to deploy the Data Ingest Dashboard application without Docker, running directly on your system with standard user privileges.

## Prerequisites

Before deploying the application rootlessly, ensure you have the following installed:

1. **Python 3.9 or later** - for the backend API
2. **Node.js 16 or later** - for the frontend
3. **pip** - Python package manager
4. **npm** - Node.js package manager

## Backend Setup (Rootless)

### 1. Install Python Dependencies

Run the setup script:
```bash
setup_backend_rootless.bat
```

Or manually install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory with the following content:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
```

### 3. Configure Firebase

Place your Firebase service account key file as `serviceAccountKey.json` in the backend directory.

### 4. Run the Backend Server

Run the backend server script:
```bash
run_backend_rootless.bat
```

Or manually start the server:
```bash
cd backend
python app.py
```

The backend will be available at `http://localhost:5000`

## Frontend Setup (Rootless)

### 1. Install Frontend Dependencies

Run the setup script:
```bash
setup_frontend_rootless.bat
```

Or manually install dependencies:
```bash
npm install
```

### 2. Configure Firebase in Frontend

Open `index.html` and locate the `firebaseConfig` object. Replace the placeholder values with your actual Firebase configuration:
```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-auth-domain",
  projectId: "your-project-id",
  storageBucket: "your-storage-bucket",
  messagingSenderId: "your-messaging-sender-id",
  appId: "your-app-id"
};
```

### 3. Run Development Server

Run the development server script:
```bash
run_frontend_dev_rootless.bat
```

Or manually start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Build for Production

To create a production build:

Run the build script:
```bash
build_frontend_rootless.bat
```

Or manually build:
```bash
npm run build
```

The built files will be in the `dist` directory.

To serve the production build:
```bash
npm install -g serve
serve -s dist -l 3000
```

## Running Both Services

To run both the frontend and backend simultaneously:

1. Start the backend server in one terminal:
   ```bash
   run_backend_rootless.bat
   ```

2. Start the frontend development server in another terminal:
   ```bash
   run_frontend_dev_rootless.bat
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
```

## Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com/
2. Generate a service account key and download the JSON file
3. Rename the file to `serviceAccountKey.json` and place it in the backend directory
4. Update the frontend `firebaseConfig` in `index.html` with your project settings

## Troubleshooting

### Common Issues

1. **Python dependencies not installing**:
   - Ensure pip is up to date: `python -m pip install --upgrade pip`
   - Try installing with user flag: `pip install --user -r requirements.txt`

2. **Node.js modules not installing**:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and package-lock.json, then run `npm install`

3. **Firebase not connecting**:
   - Verify `serviceAccountKey.json` is in the correct location
   - Check Firebase project settings and credentials
   - Ensure Firestore is enabled in your Firebase project

4. **Port conflicts**:
   - Change the backend port in `app.py`
   - Change the frontend port in `vite.config.ts`

### Windows-Specific Issues

1. **Scripts blocked by execution policy**:
   - Run PowerShell as administrator
   - Execute: `Set-ExecutionPolicy RemoteSigned`

2. **Path issues**:
   - Use forward slashes in paths or escape backslashes
   - Ensure all required files are in the correct directories

## Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Serve the built files using a web server like Nginx or Apache

3. Run the backend with a production WSGI server:
   ```bash
   cd backend
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

4. Configure your web server to proxy API requests to the backend

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Firebase Security**: Configure proper Firestore security rules
3. **Secrets Management**: Use secure methods to store and manage secrets
4. **HTTPS**: Use HTTPS in production environments
5. **CORS**: Review and configure CORS settings appropriately

## Performance Optimization

1. **Backend**:
   - Use a production WSGI server like Gunicorn
   - Implement caching for frequently accessed data
   - Optimize database queries

2. **Frontend**:
   - Minimize bundle size with code splitting
   - Implement lazy loading for large components
   - Use efficient data fetching strategies

This rootless deployment approach eliminates the need for Docker while maintaining all the functionality of the application.