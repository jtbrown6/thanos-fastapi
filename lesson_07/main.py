# Lesson 7: Sanctuary II - Background Operations
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks # Import BackgroundTasks
import httpx
from pydantic import BaseModel
from typing import Annotated
import time # Import time for simulation
import os # Import os for checking file existence

app = FastAPI()

# --- Define Pydantic Models ---

class Stone(BaseModel):
    name: str
    description: str | None = None
    acquired: bool

class Character(BaseModel):
    name: str
    affiliation: str | None = None
    power_level: int = 0

# Homework Model
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

async def verify_admin_user(current_user: CurrentUserDep):
    if current_user["username"] != "thanos":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return current_user
AdminUserDep = Annotated[dict, Depends(verify_admin_user)]

# --- Background Task Functions ---

def write_notification_log(email: str, message: str = ""):
    """ Simulates writing a log message to a file in the background. """
    log_message = f"Notification for {email}: {message}\n"
    print(f"--- BACKGROUND TASK START: Writing log: '{log_message.strip()}' ---")
    time.sleep(3) # Simulate I/O delay
    log_dir = "logs" # Define a subdirectory for logs
    os.makedirs(log_dir, exist_ok=True) # Create the directory if it doesn't exist
    file_path = os.path.join(log_dir, "notification_log.txt")
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Log written to '{file_path}' for {email} ---")

# Homework/Stretch Goal Background Task Function
def simulate_report_generation(report_request: ReportRequest): # Accepts the Pydantic model instance
    """ Simulates generating a report in the background. """
    email = report_request.recipient_email
    name = report_request.report_name
    print(f"--- BACKGROUND TASK START: Generating report '{name}' for {email} ---")
    time.sleep(5) # Simulate report generation time
    print(f"--- BACKGROUND TASK END: Report '{name}' generated for {email} ---")
    # In a real app, you might save the report or email it here.


# --- Endpoints ---
# (Keeping only a few relevant ones + new ones for Lesson 7)

@app.get("/")
async def read_root():
    return {"message": "Hello, Universe!"}

@app.get("/users/me")
async def read_current_user_endpoint(current_user: CurrentUserDep):
    return current_user

@app.get("/admin/panel")
async def read_admin_panel(admin_user: AdminUserDep):
    return {"message": f"Welcome to the Admin Panel, Lord {admin_user['username']}!"}

# --- New Endpoints for Lesson 7 ---

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks # Inject BackgroundTasks object
    ):
    """
    Sends a hypothetical notification and logs it using a background task.
    Returns a response immediately before the logging is complete.
    """
    confirmation_message = f"Notification queued for {email}"
    print(f"Endpoint '/send-notification/{email}': Preparing background task.")

    # Add the task to run after the response
    background_tasks.add_task(
        write_notification_log, # Function to call
        email,                  # Positional argument for the function
        message=confirmation_message # Keyword argument for the function
    )

    print(f"Endpoint '/send-notification/{email}': Returning response.")
    return {"message": confirmation_message}

# Homework Endpoint
@app.post("/generate-report")
async def generate_report(
    report_request: ReportRequest, # Get data from request body via Pydantic model
    background_tasks: BackgroundTasks # Inject BackgroundTasks
    ):
    """
    Starts report generation in the background based on request data.
    Returns a response immediately.
    """
    print(f"Endpoint '/generate-report': Received request for report '{report_request.report_name}' for {report_request.recipient_email}")

    # Add the background task, passing the Pydantic model instance (Stretch Goal implementation)
    background_tasks.add_task(simulate_report_generation, report_request)

    print(f"Endpoint '/generate-report': Returning response.")
    return {"message": f"Report '{report_request.report_name}' generation started for {report_request.recipient_email}."}


# To run this application:
# 1. Make sure you are in the 'lesson_07' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - POST /send-notification/test@example.com (Observe immediate response, then check terminal/log file)
#    - POST /generate-report with body:
#      {"recipient_email": "fury@shield.org", "report_name": "Avenger Initiative Budget"}
#      (Observe immediate response, then check terminal for background task messages)
