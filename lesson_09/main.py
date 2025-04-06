# Lesson 9: Batcave Security Protocols - Middleware & CORS
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware # Import CORS Middleware

import httpx
from pydantic import BaseModel, Field, EmailStr # Import Field, EmailStr
from typing import Annotated
import time
import os

app = FastAPI(
    title="Batcomputer API Interface", # Updated title
    description="API for managing Batcave resources, contacts, and intel.", # Updated description
    version="0.9.0", # Keep version for lesson context
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


# --- Define Pydantic Models (Updated) ---
class GadgetSpec(BaseModel):
    name: str = Field(..., description="The name of the gadget.")
    description: str | None = Field(None, description="Optional description of the gadget.")
    in_stock: bool = Field(..., description="Whether the gadget is currently available.")

class Contact(BaseModel):
    name: str = Field(..., description="The name of the contact.")
    affiliation: str | None = Field(None, description="Known affiliation (e.g., GCPD, Wayne Enterprises).")
    trust_level: int = Field(default=3, ge=1, le=5, description="Assessed trust level (1-5, 5=highest).")

class IntelReportRequest(BaseModel):
    recipient_email: EmailStr
    report_name: str = Field(..., description="The name or subject of the intel report.")

# --- Simulate Batcomputer Databases ---
gadget_inventory_db = {
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    2: {"name": "Grappling Hook", "type": "Mobility", "in_stock": True},
    3: {"name": "Smoke Pellet", "type": "Stealth", "in_stock": False},
    4: {"name": "Remote Hacking Device", "type": "Tech", "in_stock": True},
    5: {"name": "Explosive Gel", "type": "Demolition", "in_stock": True},
}
contacts_db = {} # Populated by POST /contacts
next_contact_id = 1

# --- Dependencies (Updated) ---
async def get_current_user():
    user_data = {"username": "batman", "email": "bruce@wayne.enterprises", "is_active": True} # Batman theme
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="User account is inactive.")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# --- Background Task Functions (Alfred's Duties - Updated) ---
def log_batcomputer_activity(user_email: str, activity: str = ""):
    log_message = f"User {user_email} activity: {activity}\n"
    print(f"--- BACKGROUND TASK START: Logging activity: '{log_message.strip()}' ---")
    time.sleep(0.5) # Faster for testing
    log_dir = "batcomputer_logs"
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "activity_log.txt")
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Activity logged to '{file_path}' for {user_email} ---")

def simulate_intel_report_compilation(report_request: IntelReportRequest):
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK START: Compiling intel report '{name}' for {email} ---")
    time.sleep(1) # Faster for testing
    print(f"--- BACKGROUND TASK END: Intel report '{name}' compiled for {email} ---")


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
    global next_contact_id # Use updated global
    for contact_data in contacts_db.values(): # Use updated DB
        if contact_data["name"].lower() == contact.name.lower():
            raise HTTPException(status_code=400, detail=f"Contact named '{contact.name}' already exists.")
    new_id = next_contact_id # Use updated global
    contacts_db[new_id] = contact.model_dump() # Use updated DB
    contacts_db[new_id]["id"] = new_id
    next_contact_id += 1 # Use updated global
    return contacts_db[new_id]

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

# --- HTML Rendering Endpoints (Updated) ---

@app.get("/batcave-display", response_class=HTMLResponse) # Updated path
async def read_batcave_display(request: Request): # Renamed function
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
    # Ensure template file exists before trying to render
    if not os.path.exists("templates/index.html"):
        raise HTTPException(status_code=500, detail="Template 'index.html' not found.")
    return templates.TemplateResponse("index.html", context)

@app.get("/contacts-view", response_class=HTMLResponse) # Updated path
async def view_contacts(request: Request): # Renamed function
    context = {
        "request": request,
        "page_title": "Contact Database", # Thematic
        "heading": "Registered Contacts", # Thematic
        "contacts": contacts_db # Use updated DB
    }
    if not contacts_db: # Use updated DB
        print("Warning: contacts_db is empty. POST to /contacts to add data.")
    # Ensure template file exists
    if not os.path.exists("templates/contacts_list.html"): # Use updated template name
         raise HTTPException(status_code=500, detail="Template 'contacts_list.html' not found.")
    return templates.TemplateResponse("contacts_list.html", context) # Use updated template name


# To run this application:
# 1. Make sure you are in the 'lesson_09' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies: `pip install "fastapi[all]"` `pip install httpx Jinja2 email-validator`
# 4. Ensure 'static' and 'templates' directories exist and contain the necessary files
#    (style.css, index.html, contacts_list.html - copy from lesson_08 if needed).
# 5. Run: `uvicorn main:app --reload`
# 6. Test endpoints via http://127.0.0.1:8000/docs
#    - Check response headers for X-Process-Time and X-API-Version.
#    - Test CORS by trying to fetch from a simple local HTML file (using fetch API)
#      if you have `origins` configured correctly (e.g., including "null" or "*").
# 7. Test HTML pages: /batcave-display, /contacts-view
