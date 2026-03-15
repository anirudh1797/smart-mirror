from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)  # male/female/other
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)  # child/teen/adult/senior
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    face_encoding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    profile_photo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="customer")
    favorites: Mapped[list["CustomerFavorite"]] = relationship(back_populates="customer")


class Stylist(Base):
    __tablename__ = "stylists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    specialties: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="stylist")


class HairstyleCategory(Base):
    __tablename__ = "hairstyle_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    hairstyles: Mapped[list["Hairstyle"]] = relationship(back_populates="category")


class Hairstyle(Base):
    __tablename__ = "hairstyles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hairstyle_categories.id"), nullable=False
    )
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    length: Mapped[str] = mapped_column(String(20), nullable=False)  # short/medium/long
    style_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    sd_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    sd_negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped["HairstyleCategory"] = relationship(back_populates="hairstyles")
    favorites: Mapped[list["CustomerFavorite"]] = relationship(back_populates="hairstyle")


class CustomerFavorite(Base):
    __tablename__ = "customer_favorites"
    __table_args__ = (
        UniqueConstraint("customer_id", "hairstyle_id", name="uq_customer_hairstyle"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    hairstyle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hairstyles.id"), nullable=False
    )
    preview_image: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="favorites")
    hairstyle: Mapped["Hairstyle"] = relationship(back_populates="favorites")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False
    )
    stylist_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("stylists.id"), nullable=True
    )
    hairstyle_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hairstyles.id"), nullable=True
    )
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[str] = mapped_column(
        String(20), default="booked"
    )  # booked/confirmed/in_progress/completed/cancelled
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    customer: Mapped["Customer"] = relationship(back_populates="appointments")
    stylist: Mapped["Stylist | None"] = relationship(back_populates="appointments")
    hairstyle: Mapped["Hairstyle | None"] = relationship()
