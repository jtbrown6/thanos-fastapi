# Lesson 6: Batcomputer Protocols - Dependency Injection
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header # Import Depends and Header
import httpx
from pydantic import BaseModel, Field
from typing import Annotated # Needed for newer FastAPI/Pydantic type hinting with Depends

app = FastAPI()

# --- Define Pydantic Models (Updated from Lesson 5) ---

class GadgetSpec(BaseModel): # Renamed from Stone
    name: str = Field(..., description="The name of the gadget.")
    description: str | None = Field(None, description="Optional description of the gadget.")
    in_stock: bool = Field(..., description="Whether the gadget is currently available.") # Renamed from acquired

class Contact(BaseModel): # Renamed from Character
    name: str = Field(..., description="The name of the contact.")
    affiliation: str | None = Field(None, description="Known affiliation (e.g., GCPD, Wayne Enterprises).")
    trust_level: int = Field(default=3, ge=1, le=5, description="Assessed trust level (1-5, 5=highest).") # Renamed from power_level, adjusted range

# --- Simulate Batcomputer Databases (from Lesson 5) ---
gadget_inventory_db = {
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    2: {"name": "Grappling Hook", "type": "Mobility", "in_stock": True},
    3: {"name": "Smoke Pellet", "type": "Stealth", "in_stock": False},
    4: {"name": "Remote Hacking Device", "type": "Tech", "in_stock": True},
    5: {"name": "Explosive Gel", "type": "Demolition", "in_stock": True},
}
contacts_db = {}
next_contact_id = 1

# --- Dependencies for Lesson 6 ---

# Simple dependency providing common query parameters
async def common_parameters(skip: int = 0, limit: int = 100):
    """ Provides common query parameters for pagination. """
    print(f"Dependency 'common_parameters' called with skip={skip}, limit={limit}")
    return {"skip": skip, "limit": limit}

# Type alias for Annotated common parameters dependency result
CommonsDep = Annotated[dict, Depends(common_parameters)]

# Dependency with yield for resource management (e.g., DB session)
async def get_db_session():
    """ Simulates acquiring and releasing a database session using yield. """
    print("==> Simulating DB connection open <==")
    db_session = {"id": hash(str(id({}))), "status": "connected", "data": {}} # Simulate unique session
    try:
        yield db_session # Value yielded is injected
    finally:
        print(f"==> Simulating DB connection close (Session ID: {db_session['id']}) <==")

DBSessionDep = Annotated[dict, Depends(get_db_session)]

# Dependency to get API Key from header (e.g., for GCPD access)
async def get_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    """ Dependency to extract an API key from the X-API-Key header. """
    print(f"API Key dependency checking header: {x_api_key}")
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing (Authentication required)")
    return x_api_key

APIKeyDep = Annotated[str, Depends(get_api_key)]

# Dependency that depends on another dependency (verify API key)
async def verify_key_and_get_user(api_key: APIKeyDep): # Depends on get_api_key implicitly via APIKeyDep
    """ Dependency that depends on get_api_key and verifies it (simulated). """
    print(f"Verifying API key: {api_key}")
    # Simulate checking the key against a known valid key
    if api_key != "gcpd-secret-key-789":
        raise HTTPException(status_code=403, detail="Invalid API Key provided (Access Denied)")
    # Simulate fetching user/permission based on key
    user_data = {"user_id": "gcpd_officer_jim", "permissions": ["read_cases"]}
    print(f"API Key verified, returning user data: {user_data}")
    return user_data

VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]

# --- Homework/Stretch Goal Dependencies ---

# Homework Dependency 1 & 3
async def get_current_user():
    """ Simulates fetching current user data. Raises error if user is inactive. """
    # Simulate fetching user data - Let's assume Batman is the default user here
    user_data = {"username": "batman", "email": "bruce@wayne.enterprises", "is_active": True}
    # user_data = {"username": "joker", "email": "ha@haha.com", "is_active": False} # Test inactive case

    print(f"Dependency 'get_current_user' returning: {user_data}")
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="User account is inactive.") # Homework 3 check
    return user_data

CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# Stretch Goal Dependency
async def verify_admin_user(current_user: CurrentUserDep): # Depends on get_current_user
    """ Verifies if the current user is the admin ('batman'). """
    print(f"Dependency 'verify_admin_user' checking user: {current_user['username']}")
    if current_user["username"] != "batman":
        raise HTTPException(status_code=403, detail="Admin privileges required. Access denied.")
    print("Admin user verified (Batman).")
    return current_user # Pass the user data along if needed

AdminUserDep = Annotated[dict, Depends(verify_admin_user)]


# --- Endpoints from Previous Lessons (mostly unchanged) ---
# (Keeping a few for context, removing others for brevity)

@app.get("/")
async def read_root():
    return {"message": "Hello, Gotham!"}

@app.get("/gadgets/{gadget_id}")
async def get_gadget_details(gadget_id: int):
    if gadget_id not in gadget_inventory_db:
        raise HTTPException(status_code=404, detail=f"Gadget with ID {gadget_id} not found in inventory.")
    return {"gadget_id": gadget_id, "status": "Located in inventory", "details": gadget_inventory_db[gadget_id]}

@app.post("/gadgets")
async def create_gadget(gadget_spec: GadgetSpec):
    for existing_gadget in gadget_inventory_db.values():
        if existing_gadget["name"].lower() == gadget_spec.name.lower():
            raise HTTPException(status_code=400, detail=f"Gadget specification for '{gadget_spec.name}' already exists.")
    return {"message": f"Gadget spec '{gadget_spec.name}' would be created (simulation).", "received_data": gadget_spec.model_dump()}

@app.post("/contacts", status_code=201)
async def create_contact(contact: Contact):
    global next_contact_id
    for contact_data in contacts_db.values():
        if contact_data["name"].lower() == contact.name.lower():
            raise HTTPException(status_code=400, detail=f"Contact named '{contact.name}' already exists.")
    new_id = next_contact_id
    contacts_db[new_id] = contact.model_dump()
    contacts_db[new_id]["id"] = new_id
    next_contact_id += 1
    return contacts_db[new_id]

# --- New Endpoints for Lesson 6 ---

@app.get("/items/") # Keeping generic path for this example
async def read_items(commons: CommonsDep): # Use the common_parameters dependency
    """ Reads generic items using common pagination parameters from Dependency Injection. """
    print(f"Endpoint '/items/' using common pagination: {commons}")
    # Simulate a large list of item IDs
    all_item_ids = [f"item_{i}" for i in range(1, 501)]
    start = commons['skip']
    end = start + commons['limit']
    paginated_items = all_item_ids[start:end]
    return {"skip": commons['skip'], "limit": commons['limit'], "items": paginated_items}

@app.get("/list-contacts/") # Changed path
async def list_contacts(commons: CommonsDep): # Reuse the common_parameters dependency
    """ Lists contacts from the simulated DB using common pagination parameters from DI. """
    print(f"Endpoint '/list-contacts/' using common pagination: {commons}")
    # Use our contacts_db keys as the list of contacts
    all_contact_ids = list(contacts_db.keys())
    start = commons['skip']
    end = start + commons['limit']
    paginated_contact_ids = all_contact_ids[start:end]
    # Fetch the actual contact data for the paginated IDs
    paginated_contacts = [contacts_db[cid] for cid in paginated_contact_ids]
    return {"skip": commons['skip'], "limit": commons['limit'], "contacts": paginated_contacts}

@app.get("/batcomputer-logs") # Changed path
async def get_logs(db: DBSessionDep): # Use the yielding dependency (simulating DB access)
    """ Reads logs using a dependency-managed DB session (simulation). """
    print(f"--- Endpoint using Batcomputer DB session ID: {db.get('id')} ---")
    # Simulate adding a log entry
    db["data"]["log_entry_1"] = "Accessed gadget inventory."
    return {"message": "Log data accessed using DB session", "session_details": db}

@app.get("/batcomputer-logs-error") # Changed path
async def get_logs_error(db: DBSessionDep): # Use the yielding dependency
    """ Simulates an error occurring while using the DB session for logs. """
    print(f"--- Endpoint (error case) using Batcomputer DB session ID: {db.get('id')} ---")
    db["data"]["log_entry_error"] = "Attempting risky operation..."
    raise HTTPException(status_code=500, detail="Batcomputer core meltdown simulated!")
    # The 'finally' block in get_db_session will still run, closing the connection.

@app.get("/gcpd-files") # Changed path
async def read_gcpd_files(current_user: VerifiedUserDep): # Use the chained dependency (verify_key_and_get_user)
     """ Accesses secure GCPD files, requiring a valid API key via dependencies. """
     print(f"Endpoint accessing GCPD files for user: {current_user.get('user_id')}")
     # Check permissions if needed from current_user['permissions']
     return {"message": "Access granted to secure GCPD files.", "accessed_by": current_user}

# --- Homework/Stretch Goal Endpoints ---

# Homework Endpoint 2
@app.get("/contacts/me") # Changed path
async def read_current_contact(current_user: CurrentUserDep): # Use the homework dependency
    """ Gets the current logged-in user's contact data (simulated). """
    print(f"Endpoint '/contacts/me' returning user: {current_user}")
    return current_user

# Stretch Goal Endpoint
@app.get("/batcave/control-panel") # Changed path
async def read_batcave_control_panel(admin_user: AdminUserDep): # Use the stretch goal dependency
    """ Accesses the Batcave control panel, requires 'batman' user via dependencies. """
    print(f"Endpoint '/batcave/control-panel' accessed by: {admin_user['username']}")
    return {"message": f"Welcome to the Batcave Control Panel, {admin_user['username'].title()}!"}


# To run this application:
# 1. Make sure you are in the 'lesson_06' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - /items/?skip=5&limit=10 (Generic pagination)
#    - /list-contacts/?limit=2 (Paginated contacts)
#    - /batcomputer-logs (Check terminal for open/close messages)
#    - /batcomputer-logs-error (Check terminal for open/close messages despite error)
#    - /gcpd-files (Try it out, add header X-API-Key: gcpd-secret-key-789)
#    - /gcpd-files (Try with wrong/missing X-API-Key header - should fail 403/401)
#    - /contacts/me (Homework - should return 'batman' user by default)
#    - /batcave/control-panel (Stretch Goal - should work as 'batman' is admin)
#    - (Optional: Modify get_current_user to return 'joker' and test /batcave/control-panel again - should fail with 403)
#    - (Optional: Modify get_current_user to set is_active=False and test /contacts/me - should fail with 400)
