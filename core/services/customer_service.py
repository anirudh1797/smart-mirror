import numpy as np
from sqlalchemy.orm import Session

from db.engine import get_session
from db.models import Customer


class CustomerService:
    """CRUD operations for customer profiles."""

    def get_all(self) -> list[Customer]:
        with get_session() as session:
            return session.query(Customer).all()

    def get_all_with_faces(self) -> list[Customer]:
        with get_session() as session:
            return (
                session.query(Customer)
                .filter(Customer.face_encoding.isnot(None))
                .all()
            )

    def get_by_id(self, customer_id: int) -> Customer | None:
        with get_session() as session:
            return session.get(Customer, customer_id)

    def create(
        self,
        name: str,
        gender: str,
        age_group: str,
        phone: str | None = None,
        email: str | None = None,
        notes: str | None = None,
        face_encoding: np.ndarray | None = None,
        profile_photo: bytes | None = None,
    ) -> Customer:
        with get_session() as session:
            customer = Customer(
                name=name,
                gender=gender,
                age_group=age_group,
                phone=phone or None,
                email=email or None,
                notes=notes,
                face_encoding=face_encoding.tobytes() if face_encoding is not None else None,
                profile_photo=profile_photo,
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer

    def update(self, customer_id: int, **kwargs) -> Customer | None:
        with get_session() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                return None

            for key, value in kwargs.items():
                if key == "face_encoding" and isinstance(value, np.ndarray):
                    setattr(customer, key, value.tobytes())
                elif hasattr(customer, key):
                    setattr(customer, key, value)

            session.commit()
            session.refresh(customer)
            return customer

    def delete(self, customer_id: int) -> bool:
        with get_session() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                return False
            session.delete(customer)
            session.commit()
            return True
