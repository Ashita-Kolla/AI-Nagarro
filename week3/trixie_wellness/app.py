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
    import os
    
    # Load environment variables if dotenv is installed
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "False").lower() in ("true", "1", "t")
    
    uvicorn.run("app:app", host=host, port=port, reload=reload)
