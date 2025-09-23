# Firestore Integration Guide

This document explains how to set up and use the Firestore integration for the ExcelInt application.

## Prerequisites

1. A Firebase project (create one at https://console.firebase.google.com/)
2. Firebase service account key file
3. Python 3.7 or higher
4. Node.js and npm (for frontend development)

## Setup Instructions

### 1. Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com/
2. In your Firebase project, go to "Project Settings" → "Service accounts"
3. Generate a new private key and download the JSON file
4. Rename the file to match your service account key filename and place it in the root directory of this project
5. The .env file should automatically reference your service account key

### 2. Environment Setup

1. The `.env` file in the root directory should contain:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=your-service-account-key.json
   ```
2. The `.gitignore` file is configured to prevent committing sensitive files

### 3. Update Frontend Configuration

1. Open `index.html` in the root directory
2. Locate the `firebaseConfig` object (around line 1435)
3. Replace the placeholder values with your actual Firebase project configuration:
   ```javascript
   const firebaseConfig = {
       apiKey: "YOUR_API_KEY",
       authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
       projectId: "YOUR_PROJECT_ID",
       storageBucket: "YOUR_PROJECT_ID.appspot.com",
       messagingSenderId: "YOUR_SENDER_ID",
       appId: "YOUR_APP_ID"
   };
   ```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Excel to Firestore Script

```bash
python excel_to_firestore.py
```

When prompted, enter the path to your Excel file (.xlsx, .xls, or .xlsm).

## How It Works

### Python Script (excel_to_firestore.py)

1. Reads Excel files using pandas with appropriate engines for different formats
2. Processes each sheet and uploads data to Firestore as separate collections
3. Automatically watches for file changes and updates Firestore in real-time (requires watchdog library)
4. Saves collection names to `collections.json` for frontend access
5. Uses environment variables for secure credential management

### React Dashboard Component

1. Connects to Firestore using the configuration in `index.html`
2. Sets up real-time listeners for all collections
3. Automatically generates appropriate charts based on data structure:
   - Bar charts for data with many columns
   - Line charts for time-series-like numerical data
   - Pie charts for categorical data
4. Updates charts in real-time when Firestore data changes

### Firestore Security Rules

The provided `firestore.rules` file implements basic security:
- Only authenticated users can read and write data
- Applies to all collections and documents

## Data Structure

- Each Excel sheet becomes a Firestore collection
- Each row in a sheet becomes a document in the collection
- Column headers become field names in the documents
- Sheet names are sanitized for Firestore collection naming requirements

## Real-time Updates

1. When you modify and save your Excel file, the Python script automatically detects changes
2. The script reprocesses the file and updates Firestore collections
3. The React Dashboard automatically receives updates through Firestore listeners
4. Charts are regenerated and updated in real-time without manual refresh

## Troubleshooting

### Common Issues

1. **Firebase Authentication Error**: Check that your `firebaseConfig` values are correct
2. **File Not Found Error**: Ensure the Excel file path is correct and accessible
3. **Permission Denied**: Verify Firestore security rules and authentication
4. **Missing Dependencies**: Install all required Python packages from `requirements.txt`

### Enabling File Watching

To enable automatic file watching, install the watchdog library:

```bash
pip install watchdog
```

## Security Considerations

1. **Never commit your service account key file** to version control
2. The `.gitignore` file is configured to prevent accidental commits of sensitive files
3. Use environment variables for credential management
4. Use Firebase security rules to restrict access as needed
5. Consider implementing more granular permissions based on your specific requirements
6. Regularly rotate your service account keys

## Customization

### Chart Types

The automatic chart selection logic can be customized in the `determineChartType` function in `Dashboard.tsx`:

- Modify conditions for different chart types
- Add new chart types by extending the logic
- Customize color schemes and styling

### Data Processing

The Python script can be extended to:
- Add data validation and cleaning
- Implement custom transformations
- Add metadata to collections
- Handle special data types (dates, currency, etc.)