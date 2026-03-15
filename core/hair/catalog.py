from sqlalchemy.orm import Session

from db.engine import get_session
from db.models import Hairstyle, HairstyleCategory


class HairstyleCatalog:
    """Queries and filters the hairstyle catalog."""

    def get_categories(self, gender: str | None = None) -> list[HairstyleCategory]:
        with get_session() as session:
            query = session.query(HairstyleCategory)
            if gender:
                query = query.filter(HairstyleCategory.gender == gender)
            return query.all()

    def get_hairstyles(
        self,
        gender: str | None = None,
        length: str | None = None,
        style_type: str | None = None,
        category_id: int | None = None,
    ) -> list[Hairstyle]:
        with get_session() as session:
            query = session.query(Hairstyle).filter(Hairstyle.is_active.is_(True))
            if gender:
                query = query.filter(Hairstyle.gender == gender)
            if length:
                query = query.filter(Hairstyle.length == length)
            if style_type:
                query = query.filter(Hairstyle.style_type == style_type)
            if category_id:
                query = query.filter(Hairstyle.category_id == category_id)
            return query.all()

    def get_by_id(self, hairstyle_id: int) -> Hairstyle | None:
        with get_session() as session:
            return session.get(Hairstyle, hairstyle_id)
