# Deployment Guide

## Quick Deployment Options

### 1. GitHub Pages (Recommended for frontend only)
1. Push your code to a GitHub repository
2. Enable GitHub Pages in repository settings
3. The included workflow will automatically build and deploy

### 2. Static Hosting Services (Frontend only)
Upload the built files to any of these services:
- **Netlify**: Drag and drop the `dist` folder after running `npm run build`
- **Vercel**: Connect your GitHub repository for automatic deployments
- **Firebase Hosting**: Use `firebase deploy` after configuring Firebase CLI

### 3. Direct File Hosting (Frontend only)
For simple deployment, you can:
1. Upload just the `index.html` file to any web server
2. The application will work as a standalone file

### 4. Full Application Deployment (Frontend + Backend)
To deploy the full application with backend capabilities:

1. Deploy the frontend using any of the methods above
2. Deploy the backend to a Python-compatible hosting service:
   - **Heroku**: Create a Procfile and deploy using Git
   - **PythonAnywhere**: Upload the backend directory and configure the WSGI file
   - **Google Cloud Run**: Containerize the application and deploy
   - **AWS Elastic Beanstalk**: Deploy as a Python application

## Build Commands

```bash
# Development
npm run dev        # Start development server at http://localhost:5173

# Production
npm run build      # Build optimized files to dist/ folder
npm run preview    # Preview the production build locally

# Backend
npm run backend:install  # Install backend dependencies
npm run backend:dev      # Start backend server at http://localhost:5000
```

## Backend Setup

1. Install Python dependencies:
   ```bash
   # Windows
   setup_backend.bat
   
   # Unix/Linux/Mac
   chmod +x setup_backend.sh
   ./setup_backend.sh
   ```

2. Set up environment variables by copying `.env.example` to `.env` and filling in the values:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. Start the backend server:
   ```bash
   # Windows
   start_backend.bat
   
   # Unix/Linux/Mac
   chmod +x start_backend.sh
   ./start_backend.sh
   ```

## Configuration

Before deployment, ensure you:
1. Replace the Firebase configuration in `index.html` with your project's config
2. Configure Firestore security rules for production use
3. Test the application with your own Firebase project
4. For backend deployment, configure environment variables properly

## Security Notes

- The current Firebase configuration is for testing only
- Set up proper Firestore security rules before production deployment
- Consider implementing user authentication for production use
- Protect your backend API endpoints with authentication in production
- Store sensitive credentials securely (use environment variables, not hardcoded values)