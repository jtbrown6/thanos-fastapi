# Lesson 8: The Batcave Display - Serving Static Assets & HTML Templates
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request # Import Request
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.templating import Jinja2Templates # Import Jinja2Templates
from fastapi.responses import HTMLResponse # Optional: Can be used for simple HTML strings

import httpx
from pydantic import BaseModel, Field, EmailStr # Import Field and EmailStr
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


# --- Define Pydantic Models (Updated) ---
class GadgetSpec(BaseModel): # Renamed from Stone
    name: str = Field(..., description="The name of the gadget.")
    description: str | None = Field(None, description="Optional description of the gadget.")
    in_stock: bool = Field(..., description="Whether the gadget is currently available.") # Renamed from acquired

class Contact(BaseModel): # Renamed from Character
    name: str = Field(..., description="The name of the contact.")
    affiliation: str | None = Field(None, description="Known affiliation (e.g., GCPD, Wayne Enterprises).")
    trust_level: int = Field(default=3, ge=1, le=5, description="Assessed trust level (1-5, 5=highest).") # Renamed from power_level

class IntelReportRequest(BaseModel): # Renamed from ReportRequest
    recipient_email: EmailStr # Use Pydantic's EmailStr for validation
    report_name: str = Field(..., description="The name or subject of the intel report.")

# --- Simulate Batcomputer Databases ---
gadget_inventory_db = { # Renamed from known_stones_db
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    2: {"name": "Grappling Hook", "type": "Mobility", "in_stock": True},
    3: {"name": "Smoke Pellet", "type": "Stealth", "in_stock": False},
    4: {"name": "Remote Hacking Device", "type": "Tech", "in_stock": True},
    5: {"name": "Explosive Gel", "type": "Demolition", "in_stock": True},
}
contacts_db = {} # Renamed from characters_db, populated by POST /contacts
next_contact_id = 1 # Renamed from next_character_id

# --- Dependencies (Updated) ---
# (Keeping only essential ones for context)
async def get_current_user():
    user_data = {"username": "batman", "email": "bruce@wayne.enterprises", "is_active": True} # Batman theme
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="User account is inactive.")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# --- Background Task Functions (Alfred's Duties - Updated) ---
def log_batcomputer_activity(user_email: str, activity: str = ""): # Renamed
    log_message = f"User {user_email} activity: {activity}\n"
    print(f"--- BACKGROUND TASK START: Logging activity: '{log_message.strip()}' ---")
    time.sleep(1) # Shorter sleep
    log_dir = "batcomputer_logs" # Thematic dir
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "activity_log.txt") # Thematic file
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Activity logged to '{file_path}' for {user_email} ---")

def simulate_intel_report_compilation(report_request: IntelReportRequest): # Renamed, uses updated model
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK START: Compiling intel report '{name}' for {email} ---")
    time.sleep(2) # Shorter sleep
    print(f"--- BACKGROUND TASK END: Intel report '{name}' compiled for {email} ---")


# --- API Endpoints (JSON focused) ---

@app.get("/")
async def read_root():
    # Keep the JSON response for the API root
    return {"message": "Welcome to the Batcomputer API Interface. Try /batcave-display for HTML view or /docs for API docs."}

# Added 'name' parameter for Stretch Goal url_for
@app.get("/gadgets/{gadget_id}", name="get_gadget_details") # Updated path and name
async def get_gadget_details(gadget_id: int): # Renamed function
    if gadget_id not in gadget_inventory_db: # Use updated DB name
        raise HTTPException(status_code=404, detail=f"Gadget with ID {gadget_id} not found in inventory.")
    return {"gadget_id": gadget_id, "status": "Located in inventory", "details": gadget_inventory_db[gadget_id]} # Use updated DB name

@app.post("/contacts", status_code=201) # Updated path
async def create_contact(contact: Contact): # Updated function name and model
    global next_contact_id # Use updated global var name
    for contact_data in contacts_db.values(): # Use updated DB name
        if contact_data["name"].lower() == contact.name.lower():
            raise HTTPException(status_code=400, detail=f"Contact named '{contact.name}' already exists.")
    new_id = next_contact_id # Use updated global var name
    contacts_db[new_id] = contact.model_dump() # Use updated DB name
    contacts_db[new_id]["id"] = new_id
    next_contact_id += 1 # Use updated global var name
    print(f"Contact added to DB: {contacts_db[new_id]}") # Updated log message
    return contacts_db[new_id]

@app.post("/log-activity/{user_email}") # Updated path
async def log_user_activity(user_email: EmailStr, background_tasks: BackgroundTasks, activity_description: str = "Generic activity logged."): # Updated function name
    confirmation_message = f"Activity logging initiated for {user_email}."
    background_tasks.add_task(log_batcomputer_activity, user_email, activity=activity_description) # Use updated task function
    return {"message": confirmation_message}

@app.post("/request-intel-report") # Updated path
async def request_intel_report(report_request: IntelReportRequest, background_tasks: BackgroundTasks): # Updated function name and model
    background_tasks.add_task(simulate_intel_report_compilation, report_request) # Use updated task function
    return {"message": f"Intel report '{report_request.report_name}' compilation requested for {report_request.recipient_email}. Alfred is on it."}

# --- HTML Rendering Endpoints for Lesson 8 ---

@app.get("/batcave-display", response_class=HTMLResponse) # Updated path
async def read_batcave_display(request: Request): # Renamed function, Inject Request object
    """ Serves the main Batcave display HTML page using Jinja2 templates. """
    # Get dynamic status based on gadget inventory
    stock_count = sum(1 for gadget in gadget_inventory_db.values() if gadget.get("in_stock"))
    total_gadgets = len(gadget_inventory_db)
    status_text = f"{stock_count}/{total_gadgets} gadget types in stock."
    status_info = {"status": status_text, "gadgets_in_stock": stock_count}

    context = {
        "request": request, # Mandatory for templates using url_for
        "page_title": "Batcave Main Display", # Thematic title
        "heading": "Welcome to the Batcave", # Thematic heading
        "status_data": status_info, # Pass updated status
        "gadgets": gadget_inventory_db # Pass gadget data instead of stones
    }
    # Assuming index.html is updated to use 'gadgets' instead of 'stones'
    return templates.TemplateResponse("index.html", context)

# Homework Endpoint
@app.get("/contacts-view", response_class=HTMLResponse) # Updated path
async def view_contacts(request: Request): # Renamed function
    """ Serves an HTML page listing contacts from the simulated database. """
    context = {
        "request": request,
        "page_title": "Contact Database", # Thematic title
        "heading": "Registered Contacts", # Thematic heading
        "contacts": contacts_db # Pass the updated contacts DB
    }
    # Ensure contacts_db is populated by POSTing to /contacts first via /docs
    if not contacts_db:
        print("Warning: contacts_db is empty. POST to /contacts to add data.")

    # Assuming character_list.html is renamed/updated to contacts_list.html
    return templates.TemplateResponse("contacts_list.html", context) # Updated template name


# To run this application:
# 1. Make sure you are in the 'lesson_08' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies: `pip install "fastapi[all]"` `pip install httpx Jinja2` `pip install python-multipart` (often needed with forms, good practice) `pip install email-validator` (for EmailStr)
# 4. Ensure 'static' and 'templates' directories exist with their files (index.html, contacts_list.html, style.css).
# 5. Run: `uvicorn main:app --reload`
# 6. Test HTML pages:
#    - http://127.0.0.1:8000/batcave-display
#    - (Optional: POST to /contacts via /docs first to add data)
#    - http://127.0.0.1:8000/contacts-view
# 7. Test static file: http://127.0.0.1:8000/static/style.css
# 8. Check API docs: http://127.0.0.1:8000/docs
