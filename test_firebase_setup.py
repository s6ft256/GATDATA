import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Load environment variables
load_dotenv()

def test_firebase_setup():
    """Test that Firebase credentials can be loaded from environment variables"""
    print("Testing Firebase setup...")
    
    # Check if environment variable is set
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"GOOGLE_APPLICATION_CREDENTIALS = {cred_path}")
    
    if not cred_path:
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        return False
    
    # Check if file exists
    if not os.path.exists(cred_path):
        print(f"ERROR: Service account key file not found at {cred_path}")
        return False
    
    print(f"SUCCESS: Service account key file found at {cred_path}")
    
    # Try to initialize Firebase
    try:
        cred = credentials.Certificate(cred_path)
        app = firebase_admin.initialize_app(cred)
        print("SUCCESS: Firebase initialized successfully")
        firebase_admin.delete_app(app)  # Clean up
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase: {e}")
        return False

if __name__ == "__main__":
    success = test_firebase_setup()
    if success:
        print("\nFirebase setup is working correctly!")
    else:
        print("\nFirebase setup has issues. Please check the configuration.")