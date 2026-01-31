import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import logging
import os

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        self.db = None
        try:
            # Check if already initialized to avoid error on re-init
            if not firebase_admin._apps:
                # 1. Try to use service account file if it exists
                cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # 2. Fallback to Application Default Credentials (Cloud Run / GCloud CLI)
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore: {e}. Using default/fallback settings.")
            self.db = None

    def get_all_users_settings(self):
        """
        Fetches all user documents from 'users' collection.
        Returns a list of dicts: [{'id': 'userId', 'preferences': {...}, 'emails': [...]}, ...]
        """
        if not self.db:
            return []

        users_data = []
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.stream()
            
            for doc in docs:
                data = doc.to_dict()
                users_data.append({
                    'id': doc.id,
                    'preferences': data.get('preferences', {}),
                    'emails': data.get('email_recipients', [])
                })
        except Exception as e:
            logger.error(f"Error fetching users from Firestore: {e}")
            return []
            
        return users_data
