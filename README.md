# Data Ingest Dashboard (Frontend with Firestore)

This is a secure, client-side web application that allows users to upload a data file (`.xlsx`, `.csv`, `.xlsm`), analyze its contents via an interactive dashboard, and send the structured data **directly to your Google Firestore database**.

The application is built with pure HTML, CSS, and JavaScript and is designed to be a universal frontend for any data ingestion pipeline that targets Firestore.

## Purpose

This application serves multiple purposes:

1. **Advanced Data Processing**: Process and clean data using Pandas and Numpy for efficient data manipulation
2. **Machine Learning Predictions**: Implement ML models with Scikit-learn to generate predictions based on uploaded data
3. **API Endpoints**: Expose RESTful API endpoints using Flask for backend services
4. **Data Visualization**: Create rich visualizations using Matplotlib, Seaborn, and Plotly

## Architecture Overview

This project consists of both frontend and backend components:

`User -> Frontend (This App) -> Flask API -> Data Processing (Pandas/Numpy) -> ML Models (Scikit-learn) -> Google Firestore`

The frontend handles user interactions, while the backend provides advanced data processing, machine learning capabilities, and API services.

## Development

This project uses Vite for development tooling:

```bash
# Install dependencies (for development tools)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Note: The application is a standalone HTML file and can be opened directly in a browser without the development server.

For a quick start guide, see [QUICK_START.md](QUICK_START.md)

## Backend API

The backend API provides advanced data processing capabilities. For detailed information about the backend, see [backend/README.md](backend/README.md).

### Tech Stack
- **Flask** for the web server
- **Pandas/Numpy** for data processing
- **Scikit-learn** for machine learning
- **Matplotlib/Seaborn/Plotly** for visualizations
- **Firebase Admin SDK** for Firestore access

### API Endpoints
- `GET /api/v1/health` - Health check endpoint
- `POST /api/v1/process-data` - Data processing and cleaning
- `POST /api/v1/visualize` - Data visualization
- `POST /api/v1/train-model` - Train ML models
- `POST /api/v1/compare-models` - Compare different ML models
- `POST /api/v1/predict` - Make ML predictions
- `POST /api/v1/upload-to-firestore` - Upload data to Firestore

## Enhanced Features

-   **Smart Header Detection**: Automatically detects and improves column headers
    - Recognizes meaningful headers like "Name", "Date", "Email", "Phone", etc.
    - Converts empty or generic headers (Column1, __EMPTY) to meaningful names
    - Infers column purpose from data content (detects dates, emails, phone numbers, amounts)
    - **Smart Header Truncation**: Automatically shortens long headers (>20 chars) with intelligent abbreviation
    - Ensures all headers are clean, unique, and Firestore-compatible
-   **Advanced Data Cleaning**: Comprehensive data cleaning with statistics
    - **Aggressive Empty Row Removal**: Removes completely empty rows and rows that are 70%+ empty
    - **Duplicate Row Detection**: Automatically identifies and removes duplicate records
    - **Smart Row Filtering**: Requires minimum meaningful content per row (2+ non-empty fields)
    - Removes empty columns and cells
    - Trims whitespace and normalizes data
    - Provides detailed cleaning statistics with breakdown by type
-   **Firebase Data Viewer**: View and browse uploaded data directly from Firestore
    - Automatically loads and displays data when switching to the tab
    - Auto-switches to data viewer after successful uploads
    - **Smart Empty Cell Handling**: Automatically hides empty cells and columns for cleaner display
    - **Toggle View**: Option to show/hide empty cells with one click
    - Browse all uploaded collections with prioritized recent uploads
    - Paginated data viewing (50 records per page)
    - Real-time collection statistics
    - Search and filter through uploaded data
-   **File Size Validation**: Enforces 10MB file size limit with clear error messages
-   **Enhanced Error Handling**: Comprehensive error handling with retry logic and specific error messages
-   **Progress Tracking**: Real-time upload progress with batch processing feedback
-   **Network Connectivity Checks**: Validates internet connection before upload attempts
-   **Automatic Retry Logic**: Handles temporary network issues with automatic retries

## Key Features

-   **Multi-Format Support:** Natively handles `.xlsx`, `.csv`, and `.xlsm` files.
-   **Direct Firestore Integration:** Uploads data directly to your Firestore database without needing a backend server.
-   **Automatic Collection Creation:** Each sheet in an Excel file (or the CSV filename) is automatically used as the name for a new Firestore collection.
-   **Efficient Batch Uploads:** Data is sent to Firestore in batches of 500 records to ensure fast and reliable performance, even with large files.
-   **Automatic Data Cleaning:** Automatically detects and removes empty rows and columns from the source file before processing.
-   **Dashboard & Analytics:** Instantly analyze your uploaded file with a rich dashboard. Drill down into individual columns with context-aware visualizations (histograms, bar charts, pie charts) and detailed statistics.
-   **Client-Side Parsing:** Files are read and parsed entirely in the browser using [SheetJS (xlsx)](https://sheetjs.com/).
-   **Modern UI:** A clean, responsive, and intuitive interface with a drag-and-drop file zone, data preview table, and clear, real-time feedback during the upload process.
-   **Zero Dependencies:** Runs entirely in the browser with no build step or package installation required.

## Setup Instructions

This application is a static website that connects to your Firebase project.

### 1. Create a Firebase Project

1.  Go to the [Firebase Console](https://console.firebase.google.com/).
2.  Click "Add project" and follow the steps to create a new project.
3.  Once your project is created, go to the project's dashboard. Click on the **Web icon** (`</>`) to add a new web app.
4.  Give your app a nickname and click "Register app".
5.  Firebase will provide you with a `firebaseConfig` object. **Copy this object.**

### 2. Configure Firestore Database

1.  In your Firebase project console, go to the **Firestore Database** section in the left-hand menu.
2.  Click "Create database".
3.  Start in **test mode** for initial setup. This allows open access for a limited time.
    > **SECURITY WARNING:** For a production application, you **must** configure [Security Rules](https://firebase.google.com/docs/firestore/security/get-started) to restrict access and protect your data.
4.  Choose a location for your database and click "Enable".

### 3. Configure the Application

1.  Clone this repository or download the `index.html` file.
2.  Open `index.html` in a text editor.
3.  Find the `firebaseConfig` object at the beginning of the main `<script type="module">` tag.
4.  **Replace the placeholder object with the one you copied from your Firebase project.

### 4. Backend Setup (Optional)

To use the advanced backend features:

1. Navigate to the backend directory: `cd backend`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file
4. Run the backend server: `python -m backend`

## How It Works

### Smart Header Detection
The application automatically improves your data headers:

1. **Header Recognition**: Scans the first few rows to identify the best header row
2. **Pattern Matching**: Recognizes common header patterns (Name, Date, Email, Phone, etc.)
3. **Data Analysis**: Infers column meaning from content when headers are missing or generic
4. **Header Cleaning**: Converts headers to clean, readable format (e.g., "Customer_Name", "Order_Date")
5. **Header Truncation**: Long headers are intelligently shortened for better display:
   - Headers longer than 20 characters are abbreviated
   - Smart abbreviation using first letters of words
   - Full header text shown on hover
   - Examples: `Data_Returned_For_Average_Training...` → `Data_Returned_F_A_T...`
6. **Uniqueness**: Ensures all headers are unique and Firestore-compatible

### Data Processing
-   **Sheet to Collection:** When you upload an Excel file, each sheet is treated as a separate dataset. The name of the sheet (e.g., "Products") is sanitized ("products") and used as the name for a Firestore collection. For CSV files, the filename is used.
-   **Row to Document:** Each row within a sheet is converted into a JSON object and uploaded as a new document in the corresponding Firestore collection. Firestore will automatically generate a unique ID for each document.
-   **Column to Field:** Each column header in your file becomes a field name in the Firestore document.

## Usage

1.  Open your deployed `index.html` file.
2.  In the "Ingest Tool" tab, drag and drop an `.xlsx`, `.csv`, or `.xlsm` file onto the upload zone.
3.  Once loaded, the "Dashboard" tab becomes available. Click it to see a visual overview and perform detailed column analysis.
4.  Return to the "Ingest Tool" tab. Preview the data for each sheet (note any data cleaning notifications).
5.  Click the "Upload All Sheets" button.
6.  The app will provide real-time feedback as it sends each sheet's data to your Firestore database.
7.  Once upload is complete, use the "Uploaded Data" tab to browse your data directly from Firebase.
8.  Check your Firebase console to see the new collections and documents.

### Using the Uploaded Data Viewer

- **Automatic Loading**: After uploading data, the app automatically switches to the "Uploaded Data" tab and loads your most recent upload
- **Manual Navigation**: 
  1. Click the "Uploaded Data" tab (enabled after first upload)
  2. Collections are automatically refreshed and the most recent one is loaded
  3. Use "Refresh Collections" button to manually reload available collections
  4. Select different collections from the dropdown to browse
  5. Use pagination controls to browse through large datasets
  6. View collection statistics including document count and last update time
- **Firebase Status**: Connection status indicator shows current Firebase connectivity
- **Debugging**: Console logs provide detailed information about data loading process
- **Collection Priority**: Recently uploaded collections appear first in the dropdown
- **Real-time Updates**: Data reflects the current state in your Firebase database