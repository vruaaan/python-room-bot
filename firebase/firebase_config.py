import firebase_admin
from firebase_admin import credentials, firestore

_db = None

def init() -> firestore.Client:
    global _db
    cred = credentials.Certificate("firebaseaccount.json")
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db

def get_db() -> firestore.Client:
    if _db is None:
        raise RuntimeError("Firebase has not been initialised. Call init() first.")
    return _db
