# Lesson 9: The Bifrost Bridge - Middleware & CORS
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware # Import CORS Middleware

import httpx
from pydantic import BaseModel
from typing import Annotated
import time
import os

app = FastAPI(
    title="FastAPI Gauntlet API",
    description="API for tracking Infinity Stones and related entities.",
    version="0.9.0", # Starting version for Lesson 9
)

# --- CORS Middleware Definition ---
# IMPORTANT: Add CORS middleware BEFORE other middleware and routes
origins = [
    "http://localhost",       # Allow standard localhost
    "http://localhost:8080",  # Allow common frontend dev port
    "http://127.0.0.1",       # Allow loopback IP
    "http://127.0.0.1:8080",  # Allow loopback IP with port
    "null",                   # Allow 'null' origin for local file testing
    # In production, replace with your actual frontend domain(s):
    # "https://your-awesome-frontend.com",
]

# Stretch Goal: More restrictive settings example (commented out)
# allowed_methods_strict = ["GET", "POST"]
# allowed_headers_strict = ["Content-Type"] # Note: Simple requests might not need Content-Type explicitly allowed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of allowed origins
    allow_credentials=True,    # Allow cookies/auth headers
    allow_methods=["*"],       # Or use allowed_methods_strict for Stretch Goal
    allow_headers=["*"],       # Or use allowed_headers_strict for Stretch Goal
)

# --- Custom Middleware Definitions ---

# Process Time Middleware (from lesson example)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """ Adds X-Process-Time header to responses. """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}" # Format as string
    print(f"Request to {request.url.path} processed in {process_time:.4f} sec")
    return response

# Homework Middleware: Add API Version Header
@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    """ Adds X-API-Version header to responses. """
    response = await call_next(request)
    response.headers["X-API-Version"] = app.version # Use version from FastAPI app instance
    return response


# --- Mount Static Files & Configure Templates ---
# Ensure these directories exist in lesson_09
if not os.path.exists("static"): os.makedirs("static")
if not os.path.exists("templates"): os.makedirs("templates")
# Copy static/style.css, templates/index.html, templates/character_list.html from lesson_08 if needed

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
characters_db = {}
next_character_id = 1

# --- Dependencies ---
async def get_current_user():
    user_data = {"username": "thanos", "email": "thanos@titan.net", "is_active": True}
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="Inactive user")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# --- Background Task Functions ---
def write_notification_log(email: str, message: str = ""):
    log_message = f"Notification for {email}: {message}\n"
    print(f"--- BACKGROUND TASK START: Writing log: '{log_message.strip()}' ---")
    time.sleep(0.5) # Faster for testing
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "notification_log.txt")
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Log written to '{file_path}' for {email} ---")

def simulate_report_generation(report_request: ReportRequest):
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK START: Generating report '{name}' for {email} ---")
    time.sleep(1) # Faster for testing
    print(f"--- BACKGROUND TASK END: Report '{name}' generated for {email} ---")


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
    global next_character_id
    for char_data in characters_db.values():
        if char_data["name"].lower() == character.name.lower():
            raise HTTPException(status_code=400, detail=f"Character named '{character.name}' already exists.")
    new_id = next_character_id
    characters_db[new_id] = character.model_dump()
    characters_db[new_id]["id"] = new_id
    next_character_id += 1
    return characters_db[new_id]

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

# --- HTML Rendering Endpoints ---

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
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
    # Ensure template file exists before trying to render
    if not os.path.exists("templates/index.html"):
        raise HTTPException(status_code=500, detail="Template 'index.html' not found.")
    return templates.TemplateResponse("index.html", context)

@app.get("/characters-view", response_class=HTMLResponse)
async def view_characters(request: Request):
    context = {
        "request": request,
        "page_title": "Character Database",
        "heading": "Registered Characters",
        "characters": characters_db
    }
    if not characters_db:
        print("Warning: characters_db is empty. POST to /characters to add data.")
    # Ensure template file exists
    if not os.path.exists("templates/character_list.html"):
         raise HTTPException(status_code=500, detail="Template 'character_list.html' not found.")
    return templates.TemplateResponse("character_list.html", context)


# To run this application:
# 1. Make sure you are in the 'lesson_09' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies: `pip install "fastapi[all]"` `pip install httpx Jinja2`
# 4. Ensure 'static' and 'templates' directories exist and contain the necessary files
#    (style.css, index.html, character_list.html - copy from lesson_08 if needed).
# 5. Run: `uvicorn main:app --reload`
# 6. Test endpoints via http://127.0.0.1:8000/docs
#    - Check response headers for X-Process-Time and X-API-Version.
#    - Test CORS by trying to fetch from a simple local HTML file (using fetch API)
#      if you have `origins` configured correctly (e.g., including "null" or "*").
