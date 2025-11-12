-- =============================================
-- pet_health_tracker_schema_fixed.sql
-- PostgreSQL 16+ compatible
-- =============================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS petcare;
SET search_path TO petcare, public;

-- === Usuarios ===
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    timezone TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION petcare.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_users_updated_at'
    ) THEN
        CREATE TRIGGER trg_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION petcare.update_updated_at();
    END IF;
END $$;

-- === Mascotas ===
CREATE TABLE IF NOT EXISTS pets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    breed TEXT,
    birth_date DATE,
    age_years INT,
    weight_kg NUMERIC(5,2),
    sex TEXT,
    photo_url TEXT,
    photo_bytea BYTEA,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_pets_updated_at
BEFORE UPDATE ON pets
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

CREATE INDEX IF NOT EXISTS idx_pets_owner ON pets(owner_id);

-- === Fotos de mascotas ===
CREATE TABLE IF NOT EXISTS pet_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    file_name TEXT,
    file_size_bytes BIGINT,
    mime_type TEXT,
    url TEXT,
    data BYTEA,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pet_photos_pet ON pet_photos(pet_id);

-- === Vacunaciones ===
CREATE TABLE IF NOT EXISTS vaccinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    vaccine_name TEXT NOT NULL,
    manufacturer TEXT,
    lot_number TEXT,
    date_administered DATE NOT NULL,
    next_due DATE,
    veterinarian TEXT,
    notes TEXT,
    proof_document_id UUID REFERENCES pet_photos(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vaccinations_pet ON vaccinations(pet_id);

-- === Desparasitaciones ===
CREATE TABLE IF NOT EXISTS dewormings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    medication TEXT,
    date_administered DATE NOT NULL,
    next_due DATE,
    veterinarian TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dewormings_pet ON dewormings(pet_id);

-- === Visitas veterinarias ===
CREATE TABLE IF NOT EXISTS vet_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    visit_date TIMESTAMPTZ NOT NULL,
    reason TEXT,
    diagnosis TEXT,
    treatment TEXT,
    follow_up_date TIMESTAMPTZ,
    veterinarian TEXT,
    documents_id UUID REFERENCES pet_photos(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vet_visits_pet ON vet_visits(pet_id);

-- === Planes de Nutrición ===
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    name TEXT,
    description TEXT,
    calories_per_day INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_nutrition_updated_at
BEFORE UPDATE ON nutrition_plans
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Comidas ===
CREATE TABLE IF NOT EXISTS meals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES nutrition_plans(id),
    meal_time TIMESTAMPTZ NOT NULL,
    description TEXT,
    calories INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_meals_pet ON meals(pet_id);

-- === Tipo ENUM para recordatorios ===
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reminder_frequency') THEN
        CREATE TYPE reminder_frequency AS ENUM ('once','daily','weekly','monthly','yearly');
    END IF;
END$$;

-- === Recordatorios ===
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pet_id UUID REFERENCES pets(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    event_time TIMESTAMPTZ NOT NULL,
    timezone TEXT,
    frequency reminder_frequency DEFAULT 'once',
    rrule TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notify_by_email BOOLEAN NOT NULL DEFAULT TRUE,
    notify_in_app BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_notified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_reminders_owner ON reminders(owner_id);
CREATE INDEX IF NOT EXISTS idx_reminders_pet ON reminders(pet_id);

-- === Notificaciones ===
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_id UUID REFERENCES reminders(id) ON DELETE SET NULL,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    pet_id UUID REFERENCES pets(id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    method TEXT,
    status TEXT,
    provider_response JSONB
);

CREATE INDEX IF NOT EXISTS idx_notifications_reminder ON notifications(reminder_id);

-- === Recuperación de contraseña ===
CREATE TABLE IF NOT EXISTS password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pwreset_user ON password_resets(user_id);

-- === Auditoría ===
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    object_type TEXT,
    object_id UUID,
    meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- === Vista de próximos recordatorios ===
CREATE OR REPLACE VIEW upcoming_reminders AS
SELECT r.*
FROM reminders r
WHERE r.is_active = TRUE
  AND (r.frequency <> 'once' OR r.event_time >= now())
  AND (r.event_time >= now() - interval '1 day')
ORDER BY r.event_time ASC;
