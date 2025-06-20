from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    birthdate = Column(Date)
    answers_json = Column(String)
    asrs_part_a_score = Column(Integer)
    asrs_part_b_score = Column(Integer)
    symptom_group = Column(String)

    sessions = relationship("Session", back_populates="user")


class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(Float, nullable=False)
    event_type = Column(String, nullable=False)
    stimulus = Column(String, nullable=True)
    response = Column(Boolean, nullable=True)

    session = relationship("Session", back_populates="events")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_uid = Column(String, unique=True, index=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    stopped_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="active")

    user = relationship("User", back_populates="sessions")
    results = relationship("Results", back_populates="session")
    events = relationship("TaskEvent", back_populates="session")


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    data = Column(String)

    session = relationship("Session", back_populates="results")
