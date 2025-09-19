import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_imports():
    """
    Test that all backend modules can be imported without errors
    """
    try:
        # Test importing the main app
        from backend import create_app
        print("✓ Main app import successful")
        
        # Test importing utils
        from backend.utils import data_processing, visualization, ml_utils, firebase_utils
        print("✓ Utility modules import successful")
        
        # Test importing API routes
        from backend.api import routes
        print("✓ API routes import successful")
        
        # Test importing config
        from backend import config
        print("✓ Config import successful")
        
        print("\nAll backend modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend module imports...")
    success = test_backend_imports()
    
    if success:
        print("\n✅ Backend setup verification passed!")
        sys.exit(0)
    else:
        print("\n❌ Backend setup verification failed!")
        sys.exit(1)