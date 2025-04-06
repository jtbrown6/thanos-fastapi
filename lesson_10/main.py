# Lesson 10: Final Preparations - Assembling & Testing Your Batcomputer API
# Application Code (Based on Lesson 9 final code)

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import httpx
from pydantic import BaseModel, Field, EmailStr # Import Field, EmailStr
from typing import Annotated
import time
import os

app = FastAPI(
    title="Batcomputer API Interface", # Updated title
    description="API for managing Batcave resources, contacts, and intel.", # Updated description
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
# WARNING: Global dictionary state makes tests dependent on execution order or requires cleanup.
# Better approaches exist (e.g., fixtures in pytest), but kept simple for the lesson.
contacts_db = {} # Renamed from characters_db
next_contact_id = 1 # Renamed from next_character_id

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
    # Use Batman theme key and user
    if api_key != "gcpd-secret-key-789":
        raise HTTPException(status_code=403, detail="Invalid API Key provided (Access Denied)")
    return {"user_id": "gcpd_officer_jim", "permissions": ["read_cases"]}
VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]

async def get_current_user():
    # Use Batman theme user
    user_data = {"username": "batman", "email": "bruce@wayne.enterprises", "is_active": True}
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="User account is inactive.")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# --- Background Task Functions ---
# Note: Background tasks might be hard to test directly without more advanced techniques
# (e.g., mocking, checking side effects like file creation).
def log_batcomputer_activity(user_email: str, activity: str = ""): # Renamed
    log_message = f"User {user_email} activity: {activity}\n"
    print(f"--- BACKGROUND TASK (SIMULATED): Logging activity: '{log_message.strip()}' ---")
    # In tests, we might not actually sleep or write files unless testing side effects.

def simulate_intel_report_compilation(report_request: IntelReportRequest): # Renamed, uses updated model
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK (SIMULATED): Compiling intel report '{name}' for {email} ---")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Batcomputer API Interface. Try /batcave-display for HTML view or /docs for API docs."} # Updated message

@app.get("/gadgets/{gadget_id}", name="get_gadget_details") # Updated path/name
async def get_gadget_details(gadget_id: int): # Renamed function
    if gadget_id not in gadget_inventory_db: # Use updated DB
        raise HTTPException(status_code=404, detail=f"Gadget with ID {gadget_id} not found in inventory.")
    return {"gadget_id": gadget_id, "status": "Located in inventory", "details": gadget_inventory_db[gadget_id]} # Use updated DB

@app.post("/contacts", status_code=201) # Updated path
async def create_contact(contact: Contact): # Updated function/model
    global next_contact_id, contacts_db # Ensure modification of global, use updated names
    # Check for duplicate name (case-insensitive)
    for contact_data in contacts_db.values(): # Use updated DB
        if contact_data["name"].lower() == contact.name.lower():
            raise HTTPException(status_code=400, detail=f"Contact named '{contact.name}' already exists.")
    # Assign ID and add to DB
    new_id = next_contact_id # Use updated global
    contacts_db[new_id] = contact.model_dump() # Use updated DB
    contacts_db[new_id]["id"] = new_id
    next_contact_id += 1 # Use updated global
    print(f"Contact added to DB: {contacts_db[new_id]}") # Updated log
    return contacts_db[new_id]

# Endpoint for clearing contacts DB (useful for testing)
@app.delete("/contacts", status_code=204) # Updated path
async def clear_contacts_db(): # Renamed function
    """ Clears the in-memory contacts database. USE WITH CAUTION (mainly for testing). """
    global contacts_db, next_contact_id # Use updated globals
    contacts_db = {} # Use updated DB
    next_contact_id = 1 # Use updated global
    print("Contacts DB cleared.") # Updated log
    return None # No content response

@app.post("/log-activity/{user_email}") # Updated path
async def log_user_activity(user_email: EmailStr, background_tasks: BackgroundTasks, activity_description: str = "Generic activity logged."): # Updated function
    confirmation_message = f"Activity logging initiated for {user_email}."
    background_tasks.add_task(log_batcomputer_activity, user_email, activity=activity_description) # Use updated task
    return {"message": confirmation_message}

@app.post("/request-intel-report") # Updated path
async def request_intel_report(report_request: IntelReportRequest, background_tasks: BackgroundTasks): # Updated function/model
    background_tasks.add_task(simulate_intel_report_compilation, report_request) # Use updated task
    return {"message": f"Intel report '{report_request.report_name}' compilation requested for {report_request.recipient_email}. Alfred is on it."}

@app.get("/contacts/me") # Updated path
async def read_current_contact_endpoint(current_user: CurrentUserDep): # Renamed function
    return current_user

@app.get("/gcpd-files") # Updated path for secure data example
async def read_gcpd_files(current_user: VerifiedUserDep): # Renamed function
     return {"message": "Access granted to secure GCPD files.", "accessed_by": current_user} # Updated message

# --- HTML Rendering Endpoints (Updated) ---

@app.get("/batcave-display", response_class=HTMLResponse) # Updated path
async def read_batcave_display(request: Request): # Renamed function
    if not templates:
         raise HTTPException(status_code=500, detail="Templates not configured.")
    stock_count = sum(1 for g in gadget_inventory_db.values() if g.get("in_stock")) # Use updated DB
    total_gadgets = len(gadget_inventory_db) # Use updated DB
    status_info = {"status": f"{stock_count}/{total_gadgets} gadget types in stock.", "gadgets_in_stock": stock_count}
    context = {
        "request": request,
        "page_title": "Batcave Main Display", # Thematic
        "heading": "Welcome to the Batcave", # Thematic
        "status_data": status_info,
        "gadgets": gadget_inventory_db # Use updated DB
    }
    if not os.path.exists("templates/index.html"):
        raise HTTPException(status_code=500, detail="Template 'index.html' not found.")
    return templates.TemplateResponse("index.html", context)

@app.get("/contacts-view", response_class=HTMLResponse) # Updated path
async def view_contacts(request: Request): # Renamed function
    if not templates:
         raise HTTPException(status_code=500, detail="Templates not configured.")
    context = {
        "request": request,
        "page_title": "Contact Database", # Thematic
        "heading": "Registered Contacts", # Thematic
        "contacts": contacts_db # Use updated DB
    }
    if not contacts_db: # Use updated DB
        print("Warning: contacts_db is empty. POST to /contacts to add data.")
    if not os.path.exists("templates/contacts_list.html"): # Use updated template name
         raise HTTPException(status_code=500, detail="Template 'contacts_list.html' not found.")
    return templates.TemplateResponse("contacts_list.html", context) # Use updated template name

# Note: Running this file directly with `python main.py` won't work correctly
# for ASGI applications like FastAPI. Use `uvicorn lesson_10.main:app --reload` from the parent directory
# or adjust paths if running from within lesson_10.
