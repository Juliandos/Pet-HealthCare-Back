import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Date, ForeignKey, Numeric, LargeBinary, BigInteger, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

# Define the ENUM for reminder_frequency
import enum
class ReminderFrequency(enum.Enum):
    once = "once"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    timezone = Column(String)
    role = Column(String, default="user")
    auth_provider = Column(String, default="local")
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    refresh_token = Column(String)
    last_login_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pets = relationship("Pet", back_populates="owner")
    reminders = relationship("Reminder", back_populates="owner")
    notifications = relationship("Notification", back_populates="owner")
    password_resets = relationship("PasswordReset", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor")

class Pet(Base):
    __tablename__ = "pets"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("petcare.users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    breed = Column(String)
    birth_date = Column(Date)
    age_years = Column(Integer)
    weight_kg = Column(Numeric(5, 2))
    sex = Column(String)
    photo_url = Column(String)
    photo_bytea = Column(LargeBinary)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    owner = relationship("User", back_populates="pets")
    photos = relationship("PetPhoto", back_populates="pet")
    vaccinations = relationship("Vaccination", back_populates="pet")
    dewormings = relationship("Deworming", back_populates="pet")
    vet_visits = relationship("VetVisit", back_populates="pet")
    nutrition_plans = relationship("NutritionPlan", back_populates="pet")
    meals = relationship("Meal", back_populates="pet")
    reminders = relationship("Reminder", back_populates="pet")
    notifications = relationship("Notification", back_populates="pet")

class PetPhoto(Base):
    __tablename__ = "pet_photos"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String)
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String)
    url = Column(String)
    data = Column(LargeBinary)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="photos")
    vaccination_proofs = relationship("Vaccination", back_populates="proof_document")
    vet_visit_documents = relationship("VetVisit", back_populates="documents")

class Vaccination(Base):
    __tablename__ = "vaccinations"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    vaccine_name = Column(String, nullable=False)
    manufacturer = Column(String)
    lot_number = Column(String)
    date_administered = Column(Date, nullable=False)
    next_due = Column(Date)
    veterinarian = Column(String)
    notes = Column(Text)
    proof_document_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pet_photos.id"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="vaccinations")
    proof_document = relationship("PetPhoto", back_populates="vaccination_proofs")

class Deworming(Base):
    __tablename__ = "dewormings"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    medication = Column(String)
    date_administered = Column(Date, nullable=False)
    next_due = Column(Date)
    veterinarian = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="dewormings")

class VetVisit(Base):
    __tablename__ = "vet_visits"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    visit_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)
    follow_up_date = Column(DateTime(timezone=True))
    veterinarian = Column(String)
    documents_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pet_photos.id"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="vet_visits")
    documents = relationship("PetPhoto", back_populates="vet_visit_documents")

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String)
    description = Column(Text)
    calories_per_day = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="nutrition_plans")
    meals = relationship("Meal", back_populates="nutrition_plan")

class Meal(Base):
    __tablename__ = "meals"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("petcare.nutrition_plans.id"))
    meal_time = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    calories = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    pet = relationship("Pet", back_populates="meals")
    nutrition_plan = relationship("NutritionPlan", back_populates="meals")

class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("petcare.users.id", ondelete="CASCADE"), nullable=False)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text)
    event_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String)
    frequency = Column(Enum(ReminderFrequency), default=ReminderFrequency.once)
    rrule = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    notify_by_email = Column(Boolean, nullable=False, default=True)
    notify_in_app = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    owner = relationship("User", back_populates="reminders")
    pet = relationship("Pet", back_populates="reminders")
    notifications = relationship("Notification", back_populates="reminder")

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("petcare.reminders.id", ondelete="SET NULL"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("petcare.users.id", ondelete="SET NULL"))
    pet_id = Column(UUID(as_uuid=True), ForeignKey("petcare.pets.id", ondelete="SET NULL"))
    sent_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    method = Column(String)
    status = Column(String)
    provider_response = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    reminder = relationship("Reminder", back_populates="notifications")
    owner = relationship("User", back_populates="notifications")
    pet = relationship("Pet", back_populates="notifications")

class PasswordReset(Base):
    __tablename__ = "password_resets"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("petcare.users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="password_resets")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {'schema': 'petcare'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("petcare.users.id"))
    action = Column(String, nullable=False)
    object_type = Column(String)
    object_id = Column(UUID(as_uuid=True))
    meta = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    actor = relationship("User", back_populates="audit_logs")