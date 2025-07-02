from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    intakes = relationship("Intake", back_populates="user")


class Intake(Base):
    __tablename__ = "intakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_uid = Column(String, nullable=False, index=True)
    answers_json = Column(String, nullable=False)
    total_score = Column(Integer, nullable=False)
    symptom_group = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="intakes")


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
    calibrations = relationship("CalibrationPoint", back_populates="session")
    features = relationship(
        "SessionFeatures", back_populates="session", uselist=False)


class CalibrationPoint(Base):
    __tablename__ = "calibration_points"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    screen_x = Column(Float, nullable=False)
    screen_y = Column(Float, nullable=False)
    measured_x = Column(Float, nullable=False)
    measured_y = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    session = relationship("Session", back_populates="calibrations")


class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(Float, nullable=False)
    event_type = Column(String, nullable=False)
    stimulus = Column(String, nullable=True)
    response = Column(Boolean, nullable=True)

    session = relationship("Session", back_populates="events")


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    data = Column(String)

    session = relationship("Session", back_populates="results")


class SessionFeatures(Base):
    __tablename__ = "session_features"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), unique=True)
    user_id = Column(Integer, nullable=True)

    # Gaze / Fixation Metrics
    mean_fixation_duration = Column(Float, nullable=True)
    fixation_count = Column(Integer, nullable=True)
    gaze_dispersion = Column(Float, nullable=True)

    # Saccade Metrics
    saccade_count = Column(Integer, nullable=True)
    saccade_rate = Column(Float, nullable=True)

    # Blink Metrics
    total_blinks = Column(Integer, nullable=True)
    blink_rate = Column(Float, nullable=True)

    # Task Performance
    go_reaction_time_mean = Column(Float, nullable=True)
    go_reaction_time_sd = Column(Float, nullable=True)
    omission_errors = Column(Integer, nullable=True)
    commission_errors = Column(Integer, nullable=True)

    # Session timestamps copy
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)

    session = relationship("Session", back_populates="features")
