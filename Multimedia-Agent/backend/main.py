"""
Main entry point for the Multimedia Agent Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.multimedia import router as multimedia_router

# --------------------------------------------------
# Create FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Educational AI Multimedia Agent",
    description="Backend API for the Multimedia Agent.",
    version="1.0.0"
)

# --------------------------------------------------
# Enable CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Serve Generated Files
# --------------------------------------------------

app.mount(
    "/outputs",
    StaticFiles(directory="backend/outputs"),
    name="outputs"
)

# --------------------------------------------------
# Register API Routes
# --------------------------------------------------

app.include_router(multimedia_router)

# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Educational AI Multimedia Agent is running 🚀"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Multimedia Agent",
        "version": "1.0.0"
    }


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )