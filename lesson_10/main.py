# Lesson 10: The Infinity Gauntlet - Assembling & Testing Your API
# Application Code (Based on Lesson 9 final code)

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import httpx
from pydantic import BaseModel
from typing import Annotated
import time
import os

app = FastAPI(
    title="FastAPI Gauntlet API",
    description="API for tracking Infinity Stones and related entities.",
    version="1.0.0", # Final Version!
)

# --- CORS Middleware Definition ---
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Custom Middleware Definitions ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(f"Request to {request.url.path} processed in {process_time:.4f} sec")
    return response

@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = app.version
    return response

# --- Mount Static Files & Configure Templates ---
# Ensure these directories exist relative to where uvicorn is run
if not os.path.exists("static"): os.makedirs("static")
if not os.path.exists("templates"): os.makedirs("templates")
# NOTE: For testing with TestClient, static/template files need to be accessible
# relative to the test execution path, or use absolute paths/more robust config.
# For simplicity, we assume tests run from the lesson_10 directory.

# Copy static/style.css, templates/index.html, templates/character_list.html from lesson_08 if needed
# This setup assumes the test runner can find these relative paths.
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
except RuntimeError as e:
    print(f"Warning: Could not mount static/templates. Ensure directories exist. Error: {e}")
    # Provide dummy objects if mounting fails, so tests requiring 'app' don't crash immediately
    templates = None # Or a mock object


# --- Define Pydantic Models ---
class Stone(BaseModel):
    name: str
    description: str | None = None
    acquired: bool

class Character(BaseModel):
    name: str
    affiliation: str | None = None
    power_level: int = 0

class ReportRequest(BaseModel):
    recipient_email: str
    report_name: str

# --- Simulate a Database ---
known_stones_db = {
    1: {"name": "Space", "location": "Tesseract", "color": "Blue", "acquired": True},
    2: {"name": "Mind", "location": "Scepter/Vision", "color": "Yellow", "acquired": True},
    3: {"name": "Reality", "location": "Aether", "color": "Red", "acquired": True},
    4: {"name": "Power", "location": "Orb/Gauntlet", "color": "Purple", "acquired": True},
    5: {"name": "Time", "location": "Eye of Agamotto", "color": "Green", "acquired": True},
    6: {"name": "Soul", "location": "Vormir/Gauntlet", "color": "Orange", "acquired": True}
}
# WARNING: Global dictionary state makes tests dependent on execution order or requires cleanup.
# Better approaches exist (e.g., fixtures in pytest), but kept simple for the lesson.
characters_db = {}
next_character_id = 1

# --- Dependencies ---
async def common_parameters(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}
CommonsDep = Annotated[dict, Depends(common_parameters)]

async def get_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    return x_api_key
APIKeyDep = Annotated[str, Depends(get_api_key)]

async def verify_key_and_get_user(api_key: APIKeyDep):
    if api_key != "fake-secret-key-123":
        raise HTTPException(status_code=403, detail="Invalid API Key provided")
    return {"user_id": "user_for_" + api_key, "permissions": ["read"]}
VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]

async def get_current_user():
    user_data = {"username": "thanos", "email": "thanos@titan.net", "is_active": True}
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="Inactive user")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# --- Background Task Functions ---
# Note: Background tasks might be hard to test directly without more advanced techniques
# (e.g., mocking, checking side effects like file creation).
def write_notification_log(email: str, message: str = ""):
    log_message = f"Notification for {email}: {message}\n"
    print(f"--- BACKGROUND TASK (SIMULATED): Writing log: '{log_message.strip()}' ---")
    # In tests, we might not actually sleep or write files unless testing side effects.

def simulate_report_generation(report_request: ReportRequest):
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK (SIMULATED): Generating report '{name}' for {email} ---")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Gauntlet API. Try /home for HTML view or /docs for API docs."}

@app.get("/stones/{stone_id}", name="get_stone_details")
async def locate_stone(stone_id: int):
    if stone_id not in known_stones_db:
        raise HTTPException(status_code=404, detail=f"Stone with ID {stone_id} not found.")
    return {"stone_id": stone_id, "status": "Located", "details": known_stones_db[stone_id]}

@app.post("/characters", status_code=201)
async def create_character(character: Character):
    global next_character_id, characters_db # Ensure modification of global
    # Check for duplicate name (case-insensitive)
    for char_data in characters_db.values():
        if char_data["name"].lower() == character.name.lower():
            raise HTTPException(status_code=400, detail=f"Character named '{character.name}' already exists.")
    # Assign ID and add to DB
    new_id = next_character_id
    characters_db[new_id] = character.model_dump()
    characters_db[new_id]["id"] = new_id
    next_character_id += 1
    print(f"Character added to DB: {characters_db[new_id]}")
    return characters_db[new_id]

# Endpoint for clearing characters DB (useful for testing)
@app.delete("/characters", status_code=204)
async def clear_characters_db():
    """ Clears the in-memory character database. USE WITH CAUTION (mainly for testing). """
    global characters_db, next_character_id
    characters_db = {}
    next_character_id = 1
    print("Character DB cleared.")
    return None # No content response

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    confirmation_message = f"Notification queued for {email}"
    background_tasks.add_task(write_notification_log, email, message=confirmation_message)
    return {"message": confirmation_message}

@app.post("/generate-report")
async def generate_report(report_request: ReportRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(simulate_report_generation, report_request)
    return {"message": f"Report '{report_request.report_name}' generation started for {report_request.recipient_email}."}

@app.get("/users/me")
async def read_current_user_endpoint(current_user: CurrentUserDep):
    return current_user

@app.get("/secure-data")
async def read_secure_data(current_user: VerifiedUserDep):
     return {"message": "This is secure data.", "accessed_by": current_user}

# --- HTML Rendering Endpoints ---

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    if not templates:
         raise HTTPException(status_code=500, detail="Templates not configured.")
    acquired_count = sum(1 for stone in known_stones_db.values() if stone.get("acquired"))
    status_text = "All stones acquired!" if acquired_count == 6 else f"Seeking {6 - acquired_count} more stones..."
    status_info = {"status": status_text, "stones_acquired": acquired_count}
    context = {
        "request": request,
        "page_title": "Knowhere Hub",
        "heading": "Welcome to the Collector's Archive!",
        "status_data": status_info,
        "stones": known_stones_db
    }
    if not os.path.exists("templates/index.html"):
        raise HTTPException(status_code=500, detail="Template 'index.html' not found.")
    return templates.TemplateResponse("index.html", context)

@app.get("/characters-view", response_class=HTMLResponse)
async def view_characters(request: Request):
    if not templates:
         raise HTTPException(status_code=500, detail="Templates not configured.")
    context = {
        "request": request,
        "page_title": "Character Database",
        "heading": "Registered Characters",
        "characters": characters_db
    }
    if not characters_db:
        print("Warning: characters_db is empty. POST to /characters to add data.")
    if not os.path.exists("templates/character_list.html"):
         raise HTTPException(status_code=500, detail="Template 'character_list.html' not found.")
    return templates.TemplateResponse("character_list.html", context)

# Note: Running this file directly with `python main.py` won't work correctly
# for ASGI applications like FastAPI. Use `uvicorn main:app --reload`.
