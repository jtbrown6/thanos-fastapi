# Lesson 8: Knowhere - Serving Static Assets & Templates
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request # Import Request
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.templating import Jinja2Templates # Import Jinja2Templates
from fastapi.responses import HTMLResponse # Optional: Can be used for simple HTML strings

import httpx
from pydantic import BaseModel
from typing import Annotated
import time
import os

app = FastAPI()

# --- Mount Static Files Directory ---
# Serve files from the 'static' directory at the '/static' URL path
# Ensure 'static' directory exists in lesson_08
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Configure Templates ---
# Tell Jinja2Templates where to find template files
# Ensure 'templates' directory exists in lesson_08
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
characters_db = {} # Will be populated by POST /characters
next_character_id = 1

# --- Dependencies ---
# (Keeping a few essential ones for context)
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
    time.sleep(1) # Shorter sleep for lesson 8
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
    time.sleep(2) # Shorter sleep for lesson 8
    print(f"--- BACKGROUND TASK END: Report '{name}' generated for {email} ---")


# --- API Endpoints (JSON focused) ---

@app.get("/")
async def read_root():
    # Redirect root to the new home page? Or keep the JSON message?
    # Let's keep the JSON for API consistency.
    return {"message": "Welcome to the FastAPI Gauntlet API. Try /home for HTML view or /docs for API docs."}

# Added 'name' parameter for Stretch Goal url_for
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
    print(f"Character added to DB: {characters_db[new_id]}")
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

# --- HTML Rendering Endpoints for Lesson 8 ---

@app.get("/home", response_class=HTMLResponse) # Specify HTMLResponse for clarity
async def read_home(request: Request): # Inject Request object
    """ Serves the main HTML homepage using Jinja2 templates. """
    acquired_count = sum(1 for stone in known_stones_db.values() if stone.get("acquired"))
    status_text = "All stones acquired!" if acquired_count == 6 else f"Seeking {6 - acquired_count} more stones..."
    status_info = {"status": status_text, "stones_acquired": acquired_count}

    context = {
        "request": request, # Mandatory for templates using url_for
        "page_title": "Knowhere Hub",
        "heading": "Welcome to the Collector's Archive!",
        "status_data": status_info,
        "stones": known_stones_db
    }
    return templates.TemplateResponse("index.html", context)

# Homework Endpoint
@app.get("/characters-view", response_class=HTMLResponse)
async def view_characters(request: Request):
    """ Serves an HTML page listing characters from the 'database'. """
    context = {
        "request": request,
        "page_title": "Character Database",
        "heading": "Registered Characters",
        "characters": characters_db # Pass the simulated DB
    }
    # Ensure characters_db is populated by POSTing to /characters first via /docs
    if not characters_db:
        print("Warning: characters_db is empty. POST to /characters to add data.")

    return templates.TemplateResponse("character_list.html", context)


# To run this application:
# 1. Make sure you are in the 'lesson_08' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies: `pip install "fastapi[all]"` `pip install httpx Jinja2`
# 4. Ensure 'static' and 'templates' directories exist with their files.
# 5. Run: `uvicorn main:app --reload`
# 6. Test HTML pages:
#    - http://127.0.0.1:8000/home
#    - (Optional: POST to /characters via /docs first)
#    - http://127.0.0.1:8000/characters-view
# 7. Test static file: http://127.0.0.1:8000/static/style.css
# 8. Check API docs: http://127.0.0.1:8000/docs
