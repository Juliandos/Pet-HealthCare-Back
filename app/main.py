from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import pets

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet HealthCare API")

app.include_router(pets.router)

@app.get("/")
def root():
    return {"message": "Pet HealthCare API is running 🚀"}
