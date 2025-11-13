from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# autocommit=False Requiere que tú llames manualmente a db.commit()
# autoflush=False Evita que SQLAlchemy sincronice los cambios con la DB antes de cada query

Base = declarative_base() # Clase base para los modelos ORM
