import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import init_db

# Import routers
from routers import chat, mood, journal, reminder, analytics, upload

app = FastAPI(title="Trixie Wellness API")

# Initialize/verify database tables on startup
init_db()

# Include routers
app.include_router(chat.router)
app.include_router(mood.router)
app.include_router(journal.router)
app.include_router(reminder.router)
app.include_router(analytics.router)
app.include_router(upload.router)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
