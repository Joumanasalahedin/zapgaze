from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    func,
    event,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date
from .database import Base
from app.utils.encryption import encrypt, decrypt, generate_pseudonym_id


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Encrypted storage columns (nullable during migration, will be NOT NULL after)
    _name_encrypted = Column("name_encrypted", String, nullable=True)
    _birthdate_encrypted = Column("birthdate_encrypted", String, nullable=True)
    pseudonym_id = Column(String, unique=True, index=True, nullable=True)

    # Legacy columns for migration (will be removed later)
    # These allow reading unencrypted data during migration
    _name_legacy = Column("name", String, nullable=True)
    _birthdate_legacy = Column("birthdate", Date, nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    intakes = relationship("Intake", back_populates="user")

    @hybrid_property
    def name(self):
        """Get decrypted name. Handles both encrypted and legacy unencrypted data."""
        if self._name_encrypted:
            try:
                return decrypt(self._name_encrypted)
            except:
                # If decryption fails, might be unencrypted (migration case)
                return (
                    self._name_encrypted
                    if self._name_encrypted
                    else (self._name_legacy or "")
                )
        # Fallback to legacy column during migration
        return self._name_legacy or ""

    @name.setter
    def name(self, value):
        """Set name - automatically encrypts the value."""
        if value:
            self._name_encrypted = encrypt(str(value))
            # Clear legacy column if it exists
            self._name_legacy = None

    @hybrid_property
    def birthdate(self):
        """Get decrypted birthdate as Date object. Handles both encrypted and legacy data."""
        if self._birthdate_encrypted:
            try:
                decrypted_str = decrypt(self._birthdate_encrypted)
                # Parse ISO format date string
                return date.fromisoformat(decrypted_str)
            except:
                # If decryption fails, might be unencrypted (migration case)
                try:
                    return date.fromisoformat(self._birthdate_encrypted)
                except:
                    pass
        # Fallback to legacy column during migration
        if self._birthdate_legacy:
            return self._birthdate_legacy
        return None

    @birthdate.setter
    def birthdate(self, value):
        """Set birthdate - automatically encrypts the value."""
        if value:
            # Convert Date to ISO string for encryption
            if isinstance(value, date):
                date_str = value.isoformat()
            else:
                date_str = str(value)
            self._birthdate_encrypted = encrypt(date_str)
            # Clear legacy column if it exists
            self._birthdate_legacy = None

    def __init__(self, **kwargs):
        """Initialize user with automatic encryption and pseudonym generation."""
        # Extract name and birthdate before calling super
        # If encrypted columns are provided directly, use them; otherwise encrypt plain values
        name_val = kwargs.pop("name", None)
        birthdate_val = kwargs.pop("birthdate", None)

        # Only set encrypted values if plain values were provided and encrypted columns aren't already set
        if name_val and "_name_encrypted" not in kwargs:
            kwargs["_name_encrypted"] = encrypt(str(name_val))
        if birthdate_val and "_birthdate_encrypted" not in kwargs:
            if isinstance(birthdate_val, date):
                date_str = birthdate_val.isoformat()
            else:
                date_str = str(birthdate_val)
            kwargs["_birthdate_encrypted"] = encrypt(date_str)

        # Generate pseudonym if not provided
        if "pseudonym_id" not in kwargs:
            kwargs["pseudonym_id"] = generate_pseudonym_id()

        super().__init__(**kwargs)


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
    features = relationship("SessionFeatures", back_populates="session", uselist=False)


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
