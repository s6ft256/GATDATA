import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import time
from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process

# Load environment variables from .env file
load_dotenv()

# Global variables for watchdog functionality
WATCHDOG_AVAILABLE = False
Observer = None
FileSystemEventHandler = None

# Try to import and set up watchdog modules
try:
    from watchdog.observers import Observer as WatchdogObserver
    from watchdog.events import FileSystemEventHandler as WatchdogEventHandler
    Observer = WatchdogObserver
    FileSystemEventHandler = WatchdogEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    print("Warning: watchdog library not available. File watching feature disabled.")

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Try to get existing app
        app = firebase_admin.get_app()
    except ValueError:
        # Initialize if not exists
        # Use service account key from environment variable
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # Fallback to default credentials
            cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(cred)
    return firestore.client()

# Process Excel file and upload to Firestore
def process_excel_to_firestore(file_path, db):
    try:
        # Determine file extension to use appropriate engine
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Read Excel file with appropriate engine
        if file_extension == '.xlsx':
            # Read Excel file with openpyxl engine for .xlsx files
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        elif file_extension in ['.xls', '.xlsm']:
            # Read Excel file with xlrd engine for .xls and .xlsm files
            excel_file = pd.ExcelFile(file_path, engine='xlrd')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Define core collection mappings with fuzzy matching patterns
        core_collections = {
            'Incidents': ['INCIDENT TRACKER', 'Incident Log', 'Safety Incidents', 'INCIDENTS', 'incident', 'accident'],
            'Inspections': ['Inspection Reports', 'Audit Results', 'Compliance Checklists', 'INSPECTIONS', 'inspection', 'audit'],
            'Trainings': ['TRAINING & COMPETENCY REGISTER', 'Induction/Training Log', 'Employee Training', 'TRAININGS', 'training', 'competency']
        }
        
        # Define extended analytics sheet patterns
        extended_analytics_patterns = [
            'MAINTENANCE', 'NEAR MISS', 'NEAR-MISS', 'SAFETY VIOLATIONS', 
            'AUDIT', 'ENVIRONMENTAL', 'WEATHER', 'EQUIPMENT'
        ]
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            # Initialize df variable
            df = None
            
            # Read sheet into DataFrame with appropriate engine
            if file_extension == '.xlsx':
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            elif file_extension in ['.xls', '.xlsm']:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
            
            # Check if df was successfully created before processing
            if df is not None:
                # Drop 'ID' column if it exists
                if 'ID' in df.columns or 'id' in df.columns:
                    df = df.drop(columns=[col for col in df.columns if col.lower() == 'id'], errors='ignore')
                
                # Clean column names (remove special characters, spaces, etc.)
                df.columns = [clean_column_name(col) for col in df.columns]
                
                # Determine target collection using fuzzy matching
                collection_name = determine_collection_name(sheet_name, core_collections, extended_analytics_patterns)
                
                # Convert DataFrame to dictionary records
                records = df.to_dict('records')
                
                # Clear existing data in collection
                clear_collection(db, collection_name)
                
                # Upload records to Firestore
                upload_records(db, collection_name, records)
            else:
                print(f"Failed to read sheet: {sheet_name}")
            
        print(f"Successfully processed {file_path}")
        # Save collection names to localStorage-compatible file
        save_collection_names(excel_file.sheet_names)
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

# Clean column names for Firestore compatibility
def clean_column_name(name):
    # Convert to string and replace problematic characters
    name = str(name)
    # Replace spaces and special characters with underscores
    cleaned = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    # If empty or starts with number, prepend underscore
    if not cleaned or cleaned[0].isdigit():
        cleaned = '_' + cleaned
    return cleaned if cleaned else 'unnamed_column'

# Sanitize collection name for Firestore
def sanitize_collection_name(name):
    # Replace spaces and special characters with underscores
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(name))
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Limit length (Firestore collection names have limits)
    sanitized = sanitized[:1500] if len(sanitized) > 1500 else sanitized
    # If empty, use default name
    return sanitized if sanitized else 'unnamed_sheet'

# Determine collection name using fuzzy matching
def determine_collection_name(sheet_name, core_collections, extended_analytics_patterns):
    # Convert sheet name to uppercase for matching
    sheet_name_upper = sheet_name.upper()
    
    # First check for exact matches (case insensitive)
    for collection, patterns in core_collections.items():
        if sheet_name_upper in [p.upper() for p in patterns] or sheet_name_upper == collection.upper():
            return collection
    
    # Then check for fuzzy matches
    best_match = None
    best_score = 0
    
    for collection, patterns in core_collections.items():
        # Check against all patterns for this collection
        for pattern in patterns:
            score = fuzz.ratio(sheet_name_upper, pattern.upper())
            if score > best_score and score >= 80:  # 80% similarity threshold
                best_score = score
                best_match = collection
    
    # If we found a good match, use it
    if best_match:
        return best_match
    
    # For extended analytics sheets, check if they match known patterns
    for pattern in extended_analytics_patterns:
        if pattern in sheet_name_upper:
            # For extended sheets, sanitize the sheet name for Firestore
            return sanitize_collection_name(sheet_name)
    
    # Default to sanitized sheet name for unrecognized sheets
    return sanitize_collection_name(sheet_name)

# Clear all documents in a collection
def clear_collection(db, collection_name):
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
    except Exception as e:
        print(f"Error clearing collection {collection_name}: {str(e)}")

# Upload records to Firestore
def upload_records(db, collection_name, records):
    try:
        collection_ref = db.collection(collection_name)
        for record in records:
            # Clean the record data
            clean_record = {}
            for key, value in record.items():
                # Handle NaN values
                if pd.isna(value):
                    clean_record[key] = None
                else:
                    clean_record[key] = value
            
            # Add document to collection
            collection_ref.add(clean_record)
    except Exception as e:
        print(f"Error uploading records to {collection_name}: {str(e)}")

# Save collection names to a file for the frontend to access
def save_collection_names(collection_names):
    try:
        # Save to a JSON file that can be accessed by the frontend
        with open('collections.json', 'w') as f:
            json.dump(collection_names, f)
    except Exception as e:
        print(f"Error saving collection names: {str(e)}")

# File system event handler for watching Excel files (only used when watchdog is available)
def create_file_handler_class():
    """Dynamically create the file handler class if watchdog is available"""
    if WATCHDOG_AVAILABLE and FileSystemEventHandler is not None:
        class ExcelFileHandler(FileSystemEventHandler):
            def __init__(self, db, file_path):
                super().__init__()
                self.db = db
                self.file_path = file_path
                
            def on_modified(self, event):
                if not event.is_directory and event.src_path == self.file_path:
                    print(f"Detected change in {self.file_path}")
                    time.sleep(1)  # Small delay to ensure file is fully written
                    process_excel_to_firestore(self.file_path, self.db)
        return ExcelFileHandler
    return None

# Main function
def main():
    # Initialize Firestore
    db = initialize_firebase()
    
    # Get Excel file path from user
    file_path = input("Enter the path to your Excel file: ").strip()
    
    # Check if file exists and has valid extension
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    valid_extensions = ['.xlsx', '.xls', '.xlsm']
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension not in valid_extensions:
        print(f"Invalid file format. Supported formats: {', '.join(valid_extensions)}")
        return
    
    # Process the file initially
    process_excel_to_firestore(file_path, db)
    
    # Set up file watcher for automatic updates (if watchdog is available)
    if WATCHDOG_AVAILABLE and Observer is not None:
        ExcelFileHandler = create_file_handler_class()
        if ExcelFileHandler is not None:
            print("Setting up file watcher for automatic updates...")
            event_handler = ExcelFileHandler(db, file_path)
            observer = Observer()
            observer.schedule(event_handler, path=os.path.dirname(file_path), recursive=False)
            observer.start()
            
            print(f"Watching {file_path} for changes. Press Ctrl+C to stop.")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                print("File watcher stopped.")
            
            observer.join()
    else:
        print("File watching feature not available. Install 'watchdog' library for automatic updates.")

if __name__ == "__main__":
    main()