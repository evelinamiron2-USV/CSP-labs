from fastapi import FastAPI
from app.routers import health

app = FastAPI(title="Global Health Application", version="1.0")

# Includem ruterul de sănătate pe care l-am creat anterior
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "Global Health API is running successfully!"}