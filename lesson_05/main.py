# Lesson 5: Contingency Plans - Handling Errors Gracefully with HTTPException
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException # Import HTTPException
import httpx
from pydantic import BaseModel, Field

app = FastAPI()

# --- Define Pydantic Models (Updated from Lesson 4) ---

class GadgetSpec(BaseModel): # Renamed from Stone
    name: str = Field(..., description="The name of the gadget.")
    description: str | None = Field(None, description="Optional description of the gadget.")
    in_stock: bool = Field(..., description="Whether the gadget is currently available.") # Renamed from acquired

class Contact(BaseModel): # Renamed from Character
    name: str = Field(..., description="The name of the contact.")
    affiliation: str | None = Field(None, description="Known affiliation (e.g., GCPD, Wayne Enterprises).")
    trust_level: int = Field(default=3, ge=1, le=5, description="Assessed trust level (1-5, 5=highest).") # Renamed from power_level, adjusted range

# --- Simulate Batcomputer Databases ---
# In a real app, this data would live in a proper database.
# We use dictionaries here for simplicity.

gadget_inventory_db = {
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    2: {"name": "Grappling Hook", "type": "Mobility", "in_stock": True},
    3: {"name": "Smoke Pellet", "type": "Stealth", "in_stock": False},
    4: {"name": "Remote Hacking Device", "type": "Tech", "in_stock": True},
    5: {"name": "Explosive Gel", "type": "Demolition", "in_stock": True},
}

# We'll store created contacts here (simulating a contacts DB)
contacts_db = {}
next_contact_id = 1

# --- Endpoints from Previous Lessons (some modified for Lesson 5) ---

@app.get("/")
async def read_root():
    return {"message": "Hello, Gotham!"}

@app.get("/status")
async def get_status():
    # Let's make status dynamic based on our gadget DB
    stock_count = sum(1 for gadget in gadget_inventory_db.values() if gadget.get("in_stock"))
    total_gadgets = len(gadget_inventory_db)
    status = f"{stock_count}/{total_gadgets} gadget types in stock."
    return {"status": status, "gadgets_in_stock": stock_count}

@app.get("/locations/{location_name}")
async def scan_location(location_name: str):
    return {"message": f"Scanning location: {location_name.title()}"}

# --- Modified for Lesson 5: GET /gadgets/{gadget_id} ---
@app.get("/gadgets/{gadget_id}")
async def get_gadget_details(gadget_id: int): # Renamed function
    """
    Retrieves details for a specific gadget by its ID from the inventory.
    Returns a 404 error if the gadget ID is not found in gadget_inventory_db.
    """
    if gadget_id not in gadget_inventory_db:
        # Raise 404 Not Found error if ID doesn't exist
        raise HTTPException(
            status_code=404, # Not Found
            detail=f"Contingency failed! Gadget with ID {gadget_id} not found in the Batcave inventory."
        )
    # If found, return the data
    gadget_data = gadget_inventory_db[gadget_id]
    return {"gadget_id": gadget_id, "status": "Located in inventory", "details": gadget_data}

@app.get("/rogues/{rogue_name}/cases/{case_id}")
async def get_rogue_case(rogue_name: str, case_id: int):
    # This remains hypothetical for now
    return {
        "rogue": rogue_name.title(),
        "case_id": case_id,
        "status": "Case file found"
        }

@app.get("/search-database")
async def search_gotham_database(keyword: str | None = None, limit: int = 10):
    if keyword:
        # Hypothetical search logic
        return {"searching_for_keyword": keyword, "results_limit": limit, "results": []}
    else:
        return {"message": "Provide a 'keyword' query parameter to search the database.", "results_limit": limit}

@app.get("/locations/{location_name}/details")
async def get_location_details(location_name: str, min_threat_level: int = 0):
    return {
        "location": location_name.title(),
        "filter_min_threat": min_threat_level,
        "data": f"Intel report for {location_name.title()} with threat level > {min_threat_level} would go here."
        }

@app.get("/fetch-posts") # External intel simulation
async def fetch_external_posts(limit: int = 5, user_id: int | None = None):
    external_api_url = "https://jsonplaceholder.typicode.com/posts"
    params = {"_limit": limit}
    if user_id is not None:
        params["userId"] = user_id
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_api_url, params=params)
            response.raise_for_status()
            external_data = response.json()
            return {
                "message": f"Successfully fetched {len(external_data)} intel reports (posts) from external source",
                "source": "JSONPlaceholder API (Simulated Intel Feed)",
                "filter_params_sent": params,
                "reports": external_data
            }
        except httpx.RequestError as exc:
             # Service Unavailable
             raise HTTPException(status_code=503, detail=f"External intel feed request failed: {exc}")
        except httpx.HTTPStatusError as exc:
             # Propagate status code, but provide context
             raise HTTPException(status_code=exc.response.status_code, detail=f"External intel feed error: {exc.response.text}")

@app.get("/filter-gadgets")
async def filter_gadgets(min_utility: int = 0, max_utility: int | None = None):
    # Hypothetical filtering based on a 'utility' key if it existed in the DB
    filtered = {gid: data for gid, data in gadget_inventory_db.items()
                if data.get('utility_level', 0) >= min_utility and \
                   (max_utility is None or data.get('utility_level', 0) <= max_utility)}
    return {
        "filtering_gadgets_by": {
            "min_utility": min_utility,
            "max_utility": max_utility if max_utility is not None else "No upper limit"
        },
        "results": filtered # Will be empty as 'utility_level' isn't in DB
    }

# --- Modified for Lesson 5 Stretch Goal: GET /fetch-contacts/{contact_id} ---
@app.get("/fetch-contacts/{contact_id}")
async def fetch_external_contact(contact_id: int): # Renamed from fetch_external_user
    """
    Fetches a specific contact from JSONPlaceholder API (simulating external DB).
    Raises 404 if the contact is not found in the external source.
    """
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{contact_id}" # Use contact_id
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_api_url)
            response.raise_for_status() # Raises exception for 4xx/5xx status codes
            contact_data = response.json()
            return {
                "message": f"Successfully fetched contact {contact_id}",
                "source": "JSONPlaceholder API (Simulated Contact DB)",
                "contact_data": contact_data
            }
        except httpx.RequestError as exc:
            # Error connecting to the external service
            raise HTTPException(status_code=503, detail=f"External contact database request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            # Handle specific errors from the external API
            if exc.response.status_code == 404:
                # If external API gives 404, we raise our own 404
                raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found in external source.")
            else:
                # For other errors, maybe return a generic server error or relay status
                raise HTTPException(status_code=502, # Bad Gateway might be appropriate
                                    detail=f"External contact database returned status {exc.response.status_code}: {exc.response.text}")


# --- Modified for Lesson 5 Homework: POST /gadgets ---
@app.post("/gadgets") # Changed path from /stones
async def create_gadget(gadget_spec: GadgetSpec): # Renamed parameter and type
    """
    Creates a new gadget specification entry.
    Raises 400 error if a gadget with the same name already exists in the inventory.
    """
    # Homework: Check if gadget name already exists (case-insensitive check)
    for existing_gadget in gadget_inventory_db.values():
        if existing_gadget["name"].lower() == gadget_spec.name.lower():
            raise HTTPException(
                status_code=400, # Bad Request
                detail=f"Gadget specification for '{gadget_spec.name}' already exists. Use PUT to update or choose a different name."
            )

    # If name is unique, proceed (in real app, generate ID and save to DB)
    print(f"Received gadget spec data: {gadget_spec}")
    # Simulate adding to DB (but gadget_inventory_db is fixed for now)
    # In a real app: new_id = db.insert(gadget_spec); return db.get(new_id)
    return {"message": f"Gadget spec '{gadget_spec.name}' would be created (simulation).", "received_data": gadget_spec.model_dump()}

# --- Modified for Lesson 5: POST /contacts ---
@app.post("/contacts", status_code=201) # Use 201 Created status code
async def create_contact(contact: Contact): # Renamed path, function, parameter, type
    """
    Creates a new contact entry in the simulated database.
    Raises 400 if a contact with the same name already exists.
    Returns the created contact with its assigned ID.
    """
    global next_contact_id # Allow modification of the global variable
    # Basic check for duplicate name (case-insensitive)
    for contact_data in contacts_db.values():
        if contact_data["name"].lower() == contact.name.lower():
            raise HTTPException(status_code=400, detail=f"Contact named '{contact.name}' already exists in the database.")

    # Assign an ID and store in our simulated DB
    new_id = next_contact_id
    contacts_db[new_id] = contact.model_dump()
    contacts_db[new_id]["id"] = new_id # Add the ID to the stored data
    next_contact_id += 1

    print(f"Created contact: {contacts_db[new_id]}")
    # Return the created contact data along with its new ID
    return contacts_db[new_id]


# To run this application:
# 1. Make sure you are in the 'lesson_05' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - GET /gadgets/1 (Success 200 - Batarang)
#    - GET /gadgets/99 (Failure 404 - Not Found)
#    - POST /gadgets with body {"name": "Sonic Emitter", "description": "Disrupts listening devices", "in_stock": true} (Success 200 - Simulation)
#    - POST /gadgets with body {"name": "Batarang", "description": "Duplicate", "in_stock": false} (Failure 400 - Already Exists)
#    - GET /fetch-contacts/1 (Success 200 - External User 1)
#    - GET /fetch-contacts/999 (Failure 404 - External User Not Found)
#    - POST /contacts with body {"name": "James Gordon", "affiliation": "GCPD", "trust_level": 5} (Success 201)
#    - POST /contacts with body {"name": "James Gordon", "affiliation": "Commissioner"} (Failure 400 - Already Exists)
