# Lesson 7: Alfred's Assistance - Background Tasks
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks # Import BackgroundTasks
import httpx
from pydantic import BaseModel, Field, EmailStr # Import EmailStr for email validation
from typing import Annotated
import time # Import time for simulation
import os # Import os for checking file existence

app = FastAPI()

# --- Define Pydantic Models (Updated from Lesson 6) ---

class GadgetSpec(BaseModel):
    name: str = Field(..., description="The name of the gadget.")
    description: str | None = Field(None, description="Optional description of the gadget.")
    in_stock: bool = Field(..., description="Whether the gadget is currently available.")

class Contact(BaseModel):
    name: str = Field(..., description="The name of the contact.")
    affiliation: str | None = Field(None, description="Known affiliation (e.g., GCPD, Wayne Enterprises).")
    trust_level: int = Field(default=3, ge=1, le=5, description="Assessed trust level (1-5, 5=highest).")

# Homework Model
class IntelReportRequest(BaseModel): # Renamed for theme
    recipient_email: EmailStr # Use Pydantic's EmailStr for validation
    report_name: str = Field(..., description="The name or subject of the intel report.")

# --- Simulate Batcomputer Databases ---
gadget_inventory_db = {
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    2: {"name": "Grappling Hook", "type": "Mobility", "in_stock": True},
    3: {"name": "Smoke Pellet", "type": "Stealth", "in_stock": False},
    4: {"name": "Remote Hacking Device", "type": "Tech", "in_stock": True},
    5: {"name": "Explosive Gel", "type": "Demolition", "in_stock": True},
}
contacts_db = {}
next_contact_id = 1

# --- Dependencies (from Lesson 6) ---

async def common_parameters(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}
CommonsDep = Annotated[dict, Depends(common_parameters)]

async def get_db_session():
    print("==> Simulating DB connection open <==")
    db_session = {"id": hash(str(id({}))), "status": "connected", "data": {}}
    try:
        yield db_session
    finally:
        print(f"==> Simulating DB connection close (Session ID: {db_session['id']}) <==")
DBSessionDep = Annotated[dict, Depends(get_db_session)]

async def get_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    return x_api_key
APIKeyDep = Annotated[str, Depends(get_api_key)]

async def verify_key_and_get_user(api_key: APIKeyDep):
    if api_key != "gcpd-secret-key-789": # Use Batman theme key
        raise HTTPException(status_code=403, detail="Invalid API Key provided (Access Denied)")
    return {"user_id": "gcpd_officer_jim", "permissions": ["read_cases"]} # Use Batman theme user
VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]

async def get_current_user():
    user_data = {"username": "batman", "email": "bruce@wayne.enterprises", "is_active": True} # Use Batman theme user
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="User account is inactive.")
    return user_data
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

async def verify_admin_user(current_user: CurrentUserDep):
    if current_user["username"] != "batman": # Use Batman theme admin
        raise HTTPException(status_code=403, detail="Admin privileges required. Access denied.")
    return current_user
AdminUserDep = Annotated[dict, Depends(verify_admin_user)]

# --- Background Task Functions (Alfred's Duties) ---

def log_batcomputer_activity(user_email: str, activity: str = ""): # Renamed function and params
    """ Simulates Alfred logging activity to the Batcomputer logs. """
    log_message = f"User {user_email} activity: {activity}\n"
    print(f"--- BACKGROUND TASK START: Logging activity: '{log_message.strip()}' ---")
    time.sleep(2) # Simulate I/O delay (Alfred is efficient)
    log_dir = "batcomputer_logs" # Thematic directory name
    os.makedirs(log_dir, exist_ok=True) # Create the directory if it doesn't exist
    file_path = os.path.join(log_dir, "activity_log.txt") # Thematic file name
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Activity logged to '{file_path}' for {user_email} ---")

# Homework/Stretch Goal Background Task Function
def simulate_intel_report_compilation(report_request: IntelReportRequest): # Accepts the updated Pydantic model
    """ Simulates Alfred compiling an intel report in the background. """
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK START: Compiling intel report '{name}' for {email} ---")
    time.sleep(5) # Simulate compilation time
    print(f"--- BACKGROUND TASK END: Intel report '{name}' compiled for {email} ---")
    # In a real app, Alfred might save the report to a secure location or encrypt it.


# --- Endpoints ---
# (Keeping only a few relevant ones + new ones for Lesson 7)

@app.get("/")
async def read_root():
    return {"message": "Hello, Gotham!"}

@app.get("/contacts/me") # Updated path
async def read_current_contact_endpoint(current_user: CurrentUserDep): # Renamed function
    return current_user

@app.get("/batcave/control-panel") # Updated path
async def read_batcave_control_panel(admin_user: AdminUserDep): # Renamed function
    return {"message": f"Welcome to the Batcave Control Panel, {admin_user['username'].title()}!"} # Updated message

# --- New Endpoints for Lesson 7 ---

@app.post("/log-activity/{user_email}") # Changed path
async def log_user_activity( # Renamed function
    user_email: EmailStr, # Use EmailStr for path param validation
    background_tasks: BackgroundTasks, # Inject BackgroundTasks object
    activity_description: str = "Generic activity logged." # Optional query param for description
    ):
    """
    Logs user activity using a background task managed by Alfred.
    Returns a response immediately before the logging is complete.
    """
    confirmation_message = f"Activity logging initiated for {user_email}."
    print(f"Endpoint '/log-activity/{user_email}': Preparing background task.")

    # Add the task to run after the response
    background_tasks.add_task(
        log_batcomputer_activity, # Function to call (Alfred's task)
        user_email,               # Positional argument for the function
        activity=activity_description # Keyword argument for the function
    )

    print(f"Endpoint '/log-activity/{user_email}': Returning response.")
    return {"message": confirmation_message}

# Homework Endpoint
@app.post("/request-intel-report") # Changed path
async def request_intel_report( # Renamed function
    report_request: IntelReportRequest, # Use updated Pydantic model
    background_tasks: BackgroundTasks # Inject BackgroundTasks
    ):
    """
    Requests Alfred to compile an intel report in the background.
    Returns a response immediately.
    """
    print(f"Endpoint '/request-intel-report': Received request for report '{report_request.report_name}' for {report_request.recipient_email}")

    # Add the background task, passing the Pydantic model instance
    background_tasks.add_task(simulate_intel_report_compilation, report_request)

    print(f"Endpoint '/request-intel-report': Returning response.")
    return {"message": f"Intel report '{report_request.report_name}' compilation requested for {report_request.recipient_email}. Alfred is on it."}


# To run this application:
# 1. Make sure you are in the 'lesson_07' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - POST /log-activity/bruce@wayne.enterprises?activity_description=Reviewed%20case%20files (Observe immediate response, then check terminal/log file in batcomputer_logs/)
#    - POST /request-intel-report with body:
#      {"recipient_email": "alfred@wayne.manor", "report_name": "Penguin's Recent Activities"}
#      (Observe immediate response, then check terminal for background task messages)
