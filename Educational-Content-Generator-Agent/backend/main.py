from fastapi import FastAPI
from api.upload import router as upload_router
from api.chat import router as chat_router

app = FastAPI(title="Educational AI Backend")

# Register the upload routes

app.include_router(upload_router)
app.include_router(chat_router)

@app.get("/")
def home():
    return {
        "message": "Educational AI Backend is running!"
    }