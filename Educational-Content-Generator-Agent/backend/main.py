from fastapi import FastAPI
from api.upload import router as upload_router
from api.chat import router as chat_router
from quiz.router import router as quiz_router
from api.flashcards import router as flashcards_router

app = FastAPI(title="Educational AI Backend")

# Register routes
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(quiz_router)
app.include_router(flashcards_router)

@app.get("/")
def home():
    return {
        "message": "Educational AI Backend is running!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)