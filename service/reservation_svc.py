from datetime import date, datetime

from model.reservation import Reservation
from service.firestore_svc import FirestoreSvc

COLLECTION = "reservations"


class ReservationSvc: #Additional layer that utilises CRUD functions from FirestoreSvc."""

    def __init__(self, store: FirestoreSvc):
        self.store = store

    def create(self, reservation: Reservation) -> str:
        return self.store.save(COLLECTION, reservation.to_payload())

    def delete_past(self) -> None:
        now = datetime.now()
        passed = [r for r in self.find_all() if r.passed(now)]
        for reservation in passed:
            self.store.delete(COLLECTION, reservation.id)

    def delete(self, booking_id: str) -> None:
        self.store.delete(COLLECTION, booking_id)

    def find_all(self) -> list[Reservation]:
        return self._db_to_res(self.store.find_all(COLLECTION))

    def find_by_venue(self, venue: str) -> list[Reservation]:
        return self._db_to_res(self.store.find_where(COLLECTION, "venue", venue))

    def find_by_date(self, d: date) -> list[Reservation]:
        return self._db_to_res(self.store.find_where(COLLECTION, "date_start", d.isoformat()))

    def find_by_user(self, tele_handle: str) -> list[Reservation]:
        return self._db_to_res(self.store.find_where(COLLECTION, "telehandle", tele_handle))

    def has_conflict(self, candidate: Reservation) -> bool:
        return any(candidate.clashing(r) for r in self.find_by_venue(candidate.venue))

    @staticmethod
    def _db_to_res(docs) -> list[Reservation]:
        return [Reservation.from_doc(d) for d in docs]
