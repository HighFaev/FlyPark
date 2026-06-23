from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="client")
    imie = Column(String(100), nullable=True)
    nazwisko = Column(String(100), nullable=True)
    telefon = Column(String(30), nullable=True)

    reservations = relationship("Reservation", back_populates="user")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    imie = Column(String(100), nullable=False)
    nazwisko = Column(String(100), nullable=False)
    telefon = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False)
    nr_rej_pojazdu = Column(String(20), nullable=False)
    nr_lotu_powrotnego = Column(String(20), nullable=True)
    liczba_osob = Column(Integer, nullable=False, default=1)
    odbior_z_lotniska = Column(Boolean, nullable=False, default=False)

    data_przyjazdu = Column(DateTime, nullable=False)
    data_wyjazdu = Column(DateTime, nullable=False)
    typ_miejsca = Column(String(20), nullable=False, default="standard")

    koszt = Column(Numeric(10, 2), nullable=False, default=0)
    oplacony = Column(Boolean, nullable=False, default=False)
    forma_platnosci = Column(String(30), nullable=True)
    status = Column(String(20), nullable=False, default="aktywna")
    uwagi = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="reservations")


class PriceItem(Base):
    __tablename__ = "price_items"

    id = Column(Integer, primary_key=True)
    kod = Column(String(40), unique=True, nullable=False)
    nazwa = Column(String(120), nullable=False)
    cena = Column(Numeric(10, 2), nullable=False)
