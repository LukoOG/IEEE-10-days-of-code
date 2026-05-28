from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.notes import router as notes_router

app = FastAPI(
    title="Notes API",
    description="IEE CS UNILAG 10 days of Code challenge",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/")
def home():
    return {"message": "Notes API is running"}


