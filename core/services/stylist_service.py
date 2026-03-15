from db.engine import get_session
from db.models import Stylist


class StylistService:
    """CRUD operations for stylists."""

    def get_all_active(self) -> list[Stylist]:
        with get_session() as session:
            return session.query(Stylist).filter(Stylist.is_active.is_(True)).all()

    def get_by_id(self, stylist_id: int) -> Stylist | None:
        with get_session() as session:
            return session.get(Stylist, stylist_id)

    def create(self, name: str, phone: str | None = None, specialties: str | None = None) -> Stylist:
        with get_session() as session:
            stylist = Stylist(name=name, phone=phone, specialties=specialties)
            session.add(stylist)
            session.commit()
            session.refresh(stylist)
            return stylist

    def seed_default(self) -> None:
        """Create a default stylist if none exist."""
        with get_session() as session:
            if session.query(Stylist).count() == 0:
                session.add(Stylist(name="Default Stylist", is_active=True))
                session.commit()
