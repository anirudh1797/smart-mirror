from datetime import date, time

from db.engine import get_session
from db.models import Appointment


class AppointmentService:
    """CRUD and scheduling for appointments."""

    def create(
        self,
        customer_id: int,
        appointment_date: date,
        appointment_time: time,
        stylist_id: int | None = None,
        hairstyle_id: int | None = None,
        duration_minutes: int = 60,
        notes: str | None = None,
    ) -> Appointment:
        with get_session() as session:
            appt = Appointment(
                customer_id=customer_id,
                stylist_id=stylist_id,
                hairstyle_id=hairstyle_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=duration_minutes,
                notes=notes,
                status="booked",
            )
            session.add(appt)
            session.commit()
            session.refresh(appt)
            return appt

    def get_by_customer(self, customer_id: int) -> list[Appointment]:
        with get_session() as session:
            return (
                session.query(Appointment)
                .filter(Appointment.customer_id == customer_id)
                .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
                .all()
            )

    def get_upcoming(self, from_date: date | None = None) -> list[Appointment]:
        if from_date is None:
            from_date = date.today()
        with get_session() as session:
            return (
                session.query(Appointment)
                .filter(
                    Appointment.appointment_date >= from_date,
                    Appointment.status.in_(["booked", "confirmed"]),
                )
                .order_by(Appointment.appointment_date, Appointment.appointment_time)
                .all()
            )

    def update_status(self, appointment_id: int, status: str) -> Appointment | None:
        with get_session() as session:
            appt = session.get(Appointment, appointment_id)
            if appt:
                appt.status = status
                session.commit()
                session.refresh(appt)
            return appt
