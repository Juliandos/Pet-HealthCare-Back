-- =============================================
-- pet_health_tracker_schema.sql (versión corregida y completa)
-- PostgreSQL 16+ - limpio y listo desde cero
-- =============================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- === Crear esquema ===
CREATE SCHEMA IF NOT EXISTS petcare AUTHORIZATION petuser;
SET search_path TO petcare, public;

-- === Función para actualizar "updated_at" ===
CREATE OR REPLACE FUNCTION petcare.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- === Tabla: usuarios ===
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    timezone TEXT,
    role TEXT DEFAULT 'user',
    auth_provider TEXT DEFAULT 'local',
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    failed_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ,
    refresh_token TEXT,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: mascotas ===
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

CREATE INDEX idx_pets_owner ON pets(owner_id);

-- === Tabla: fotos de mascotas ===
CREATE TABLE IF NOT EXISTS pet_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    file_name TEXT,
    file_size_bytes BIGINT,
    mime_type TEXT,
    url TEXT,
    data BYTEA,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_pet_photos_updated_at
BEFORE UPDATE ON pet_photos
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: vacunas ===
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
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_vaccinations_updated_at
BEFORE UPDATE ON vaccinations
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: desparasitaciones ===
CREATE TABLE IF NOT EXISTS dewormings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    medication TEXT,
    date_administered DATE NOT NULL,
    next_due DATE,
    veterinarian TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_dewormings_updated_at
BEFORE UPDATE ON dewormings
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: visitas veterinarias ===
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
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_vet_visits_updated_at
BEFORE UPDATE ON vet_visits
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: planes de nutrición ===
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

-- === Tabla: comidas ===
CREATE TABLE IF NOT EXISTS meals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES nutrition_plans(id),
    meal_time TIMESTAMPTZ NOT NULL,
    description TEXT,
    calories INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_meals_updated_at
BEFORE UPDATE ON meals
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tipos ENUM y recordatorios ===
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reminder_frequency') THEN
        CREATE TYPE reminder_frequency AS ENUM ('once','daily','weekly','monthly','yearly');
    END IF;
END$$;

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
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_reminders_updated_at
BEFORE UPDATE ON reminders
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: notificaciones ===
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_id UUID REFERENCES reminders(id) ON DELETE SET NULL,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    pet_id UUID REFERENCES pets(id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    method TEXT,
    status TEXT,
    provider_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_notifications_updated_at
BEFORE UPDATE ON notifications
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: restablecimiento de contraseñas ===
CREATE TABLE IF NOT EXISTS password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_password_resets_updated_at
BEFORE UPDATE ON password_resets
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Tabla: logs de auditoría ===
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    object_type TEXT,
    object_id UUID,
    meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_audit_logs_updated_at
BEFORE UPDATE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION petcare.update_updated_at();

-- === Vista: recordatorios próximos ===
CREATE OR REPLACE VIEW upcoming_reminders AS
SELECT r.*
FROM reminders r
WHERE r.is_active = TRUE
  AND (r.frequency <> 'once' OR r.event_time >= now())
  AND (r.event_time >= now() - interval '1 day')
ORDER BY r.event_time ASC;
