from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Render usa postgres:// pero SQLAlchemy necesita postgresql+psycopg2://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Configuración del engine con opciones para producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=300,    # Reciclar conexiones cada 5 minutos
    pool_size=10,        # Número de conexiones en el pool
    max_overflow=20,     # Conexiones adicionales permitidas
    echo=False           # No mostrar SQL en producción (cambiar a True para debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Local
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # autocommit=False Requiere que tú llames manualmente a db.commit()
# # autoflush=False Evita que SQLAlchemy sincronice los cambios con la DB antes de cada query

# Base = declarative_base() # Clase base para los modelos ORM
