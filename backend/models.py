# backend/models.py
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from backend.database import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    short_name = Column(String)
    type = Column(String)
    province = Column(String)


class Bursary(Base):
    __tablename__ = "bursaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    provider = Column(String)
    field_of_study = Column(String)
    opening_date = Column(Date)
    closing_date = Column(Date)
    description = Column(String)
    website = Column(String)
    is_active = Column(Boolean, default=True)


class Programme(Base):
    __tablename__ = "programmes"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String, index=True)
    faculty = Column(String)
    department = Column(String)
    programme = Column(String, index=True)
    score_type = Column(String, nullable=True)
    aps_score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    entry_requirement = Column(String)
    notes = Column(String)
    source = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SavedProgramme(Base):
    __tablename__ = "saved_programmes"
    __table_args__ = (
        UniqueConstraint("user_id", "programme_id", name="uq_saved_user_programme"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    programme_id = Column(Integer, ForeignKey("programmes.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)