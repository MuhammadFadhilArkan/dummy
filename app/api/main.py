from fastapi import FastAPI
from .routers import cfaAPI
import logging
logger = logging.getLogger("gunicorn.error")

app = FastAPI()
app.include_router(cfaAPI.router)

@app.get("/")
def root():
    return {"message": "This is CounterFactual Analytics Backend"}
