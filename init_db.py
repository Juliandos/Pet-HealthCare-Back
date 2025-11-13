"""
Script para inicializar la base de datos en Render
Ejecutar con: python init_db.py
"""
import os
from sqlalchemy import create_engine, text
from app.database import Base, engine
from app.models import *
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Inicializa la base de datos con el esquema y configuración"""
    
    print("🔧 Iniciando configuración de base de datos...")
    
    # Obtener URL de la base de datos
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return
    
    # Render usa postgresql:// pero SQLAlchemy necesita postgresql+psycopg2://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    
    print(f"📍 Conectando a base de datos...")
    
    try:
        # Crear engine temporal para ejecutar comandos SQL directos
        temp_engine = create_engine(database_url)
        
        with temp_engine.connect() as conn:
            # Crear extensión pgcrypto si no existe
            print("🔐 Creando extensión pgcrypto...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
            
            # Crear esquema petcare si no existe
            print("📁 Creando esquema petcare...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS petcare;"))
            
            # Crear función para updated_at
            print("⚙️ Creando función update_updated_at...")
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION petcare.update_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                  NEW.updated_at = now();
                  RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            # Crear tipo ENUM si no existe
            print("📝 Creando tipos ENUM...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reminder_frequency') THEN
                        CREATE TYPE petcare.reminder_frequency AS ENUM ('once','daily','weekly','monthly','yearly');
                    END IF;
                END$$;
            """))
            
            conn.commit()
            print("✅ Configuración base completada")
        
        # Crear todas las tablas usando SQLAlchemy
        print("🏗️ Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        # Crear vista upcoming_reminders
        with temp_engine.connect() as conn:
            print("👁️ Creando vistas...")
            conn.execute(text("""
                CREATE OR REPLACE VIEW petcare.upcoming_reminders AS
                SELECT r.*
                FROM petcare.reminders r
                WHERE r.is_active = TRUE
                  AND (r.frequency <> 'once' OR r.event_time >= now())
                  AND (r.event_time >= now() - interval '1 day')
                ORDER BY r.event_time ASC;
            """))
            conn.commit()
            print("✅ Vistas creadas exitosamente")
        
        print("\n🎉 ¡Base de datos inicializada correctamente!")
        print("✅ Puedes iniciar la aplicación con: uvicorn app.main:app")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()