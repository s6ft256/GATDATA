import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import os

class FirestoreManager:
    def __init__(self, credentials_path=None):
        """
        Initialize Firestore manager
        """
        if not firebase_admin._apps:
            try:
                if credentials_path and os.path.exists(credentials_path):
                    cred = credentials.Certificate(credentials_path)
                else:
                    # Try to use default credentials
                    cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            except Exception as e:
                # If both methods fail, try without credentials (for development)
                try:
                    firebase_admin.initialize_app()
                except Exception as e2:
                    raise Exception(f"Failed to initialize Firebase: {str(e)} and {str(e2)}")
        
        self.db = firestore.client()
    
    def upload_dataframe(self, df, collection_name, batch_size=500):
        """
        Upload a pandas DataFrame to Firestore
        """
        # Convert DataFrame to dictionary records
        records = df.to_dict(orient='records')
        
        # Upload in batches
        for i in range(0, len(records), batch_size):
            batch = self.db.batch()
            batch_records = records[i:i+batch_size]
            
            for j, record in enumerate(batch_records):
                doc_ref = self.db.collection(collection_name).document(f'record_{i+j}')
                batch.set(doc_ref, record)
            
            batch.commit()
        
        return f"Uploaded {len(records)} records to {collection_name}"
    
    def download_collection(self, collection_name):
        """
        Download a Firestore collection to a pandas DataFrame
        """
        try:
            docs = self.db.collection(collection_name).stream()
            records = []
            
            for doc in docs:
                record = doc.to_dict()
                record['id'] = doc.id
                records.append(record)
            
            df = pd.DataFrame(records)
            return df
        except Exception as e:
            raise Exception(f"Failed to download collection {collection_name}: {str(e)}")
    
    def query_collection(self, collection_name, field, operator, value):
        """
        Query a Firestore collection
        """
        try:
            docs = self.db.collection(collection_name).where(field, operator, value).stream()
            records = []
            
            for doc in docs:
                record = doc.to_dict()
                record['id'] = doc.id
                records.append(record)
            
            df = pd.DataFrame(records)
            return df
        except Exception as e:
            raise Exception(f"Failed to query collection {collection_name}: {str(e)}")

def initialize_firebase(credentials_path=None):
    """
    Initialize Firebase Admin SDK
    """
    if not firebase_admin._apps:
        try:
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
            else:
                # Try to use default credentials
                cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        except Exception as e:
            # If both methods fail, try without credentials (for development)
            try:
                firebase_admin.initialize_app()
            except Exception as e2:
                raise Exception(f"Failed to initialize Firebase: {str(e)} and {str(e2)}")
    
    return firestore.client()