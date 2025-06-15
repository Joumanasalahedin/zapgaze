from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    birthdate = Column(Date)
    answers_json = Column(String)  # Store full answers as JSON string
    asrs_part_a_score = Column(Integer)
    asrs_part_b_score = Column(Integer)
    symptom_group = Column(String)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_uid = Column(String, unique=True, index=True)

    user = relationship("User", back_populates="sessions")
    results = relationship("Results", back_populates="session")


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    data = Column(String)

    session = relationship("Session", back_populates="results")
