from google.cloud.firestore_v1 import Client, DocumentSnapshot
from typing import Any


class FirestoreSvc: # basic CRUD operations for Firestore 

    def __init__(self, db: Client):
        self.db = db

    def save(self, collection: str, data: dict[str, Any]) -> str:
        ref = self.db.collection(collection).document()
        ref.set(data)
        return ref.id

    def find_all(self, collection: str) -> list[DocumentSnapshot]:
        return list(self.db.collection(collection).stream())

    def find_where(self, collection: str, field: str, value: Any) -> list[DocumentSnapshot]:
        return list(self.db.collection(collection).where(field, "==", value).stream())

    def find_by_id(self, collection: str, document_id: str) -> DocumentSnapshot:
        return self.db.collection(collection).document(document_id).get()

    def delete(self, collection: str, document_id: str) -> None:
        self.db.collection(collection).document(document_id).delete()
