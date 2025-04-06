# Lesson 4: The Utility Belt - Structuring Data with Pydantic Models
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI
import httpx
from pydantic import BaseModel, Field # Import Pydantic's BaseModel and Field

app = FastAPI()

# --- Define Pydantic Models (Data Blueprints) ---
# These classes define the expected structure and types for data in request bodies,
# like blueprints for gadgets or case files.

class CaseFile(BaseModel):
    case_name: str = Field(..., description="The unique name or identifier for the case.") # Required string field
    details: str | None = Field(None, description="Optional details or summary of the case.") # Optional string field
    is_open: bool = Field(..., description="Whether the case is currently active/open.") # Required boolean field

class RogueProfile(BaseModel): # Homework Model
    alias: str = Field(..., description="The known alias of the rogue.") # Required string field
    status: str | None = Field(None, description="Current known status (e.g., 'At Large', 'Incarcerated').") # Optional string field
    threat_level: int = Field(default=1, ge=1, le=10, description="Assessed threat level (1-10).") # Integer field with default and validation

# --- Endpoints from Previous Lessons (Updated for Theme) ---

# --- Endpoints from Previous Lessons (for context) ---

@app.get("/")
async def read_root():
    return {"message": "Hello, Gotham!"}

@app.get("/status")
async def get_status():
    return {"status": "Protecting Gotham"}

@app.get("/locations/{location_name}")
async def scan_location(location_name: str):
    return {"message": f"Scanning location: {location_name.title()}"}

@app.get("/gadgets/{gadget_id}")
async def get_gadget(gadget_id: int):
    # Note: This endpoint currently just returns the ID.
    # We'll make it more useful later when we have stored data.
    return {"gadget_id": gadget_id, "status": "Available (hypothetically)"}

@app.get("/rogues/{rogue_name}/cases/{case_id}")
async def get_rogue_case(rogue_name: str, case_id: int):
    return {
        "rogue": rogue_name.title(),
        "case_id": case_id,
        "status": "Case file found"
        }

@app.get("/search-database")
async def search_gotham_database(keyword: str | None = None, limit: int = 10):
    if keyword:
        return {"searching_for_keyword": keyword, "results_limit": limit}
    else:
        return {"message": "Provide a 'keyword' query parameter to search the database.", "results_limit": limit}

@app.get("/locations/{location_name}/details")
async def get_location_details(location_name: str, min_threat_level: int = 0):
    return {
        "location": location_name.title(),
        "filter_min_threat": min_threat_level,
        "data": f"Intel report for {location_name.title()} with threat level > {min_threat_level} would go here."
        }

@app.get("/fetch-posts") # Keeping generic as it's external simulation
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
        # Basic error handling
        except httpx.RequestError as exc:
            return {"error": "Failed to fetch intel from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            return {"error": f"External intel source returned status {exc.response.status_code}", "details": exc.response.text}

@app.get("/filter-gadgets")
async def filter_gadgets(min_utility: int = 0, max_utility: int | None = None):
    return {
        "filtering_gadgets_by": {
            "min_utility": min_utility,
            "max_utility": max_utility if max_utility is not None else "No upper limit"
        }
    }

@app.get("/fetch-contacts/{contact_id}")
async def fetch_external_contact(contact_id: int):
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{contact_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_api_url)
            response.raise_for_status()
            contact_data = response.json()
            return {
                "message": f"Successfully fetched contact {contact_id}",
                "source": "JSONPlaceholder API (Simulated Contact DB)",
                "contact_data": contact_data
            }
        # Basic error handling
        except httpx.RequestError as exc:
            return {"error": "Failed to fetch contact data from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            return {"error": f"External API returned status {exc.response.status_code} (Contact likely not found)", "contact_id_requested": contact_id}


# --- New Endpoints for Lesson 4: Receiving Structured Data ---

@app.post("/cases") # Changed path from /stones
async def create_case(case_file: CaseFile): # Expects JSON body matching the CaseFile model
    """
    Creates a new case file entry based on the provided data.
    FastAPI uses the 'CaseFile' Pydantic model to validate the request body automatically.
    If validation fails, FastAPI returns a 422 error.
    """
    print(f"Received case file data: {case_file}") # Pydantic models have nice string representations

    # In a real application, you would typically save the validated 'case_file' data
    # (e.g., case_file.case_name, case_file.details, case_file.is_open) to a database.
    # For now, we just print it and return it.

    # Use .model_dump() (Pydantic v2+) or .dict() (Pydantic v1) to get a dictionary representation
    return {"message": f"Case File '{case_file.case_name}' created successfully.", "received_data": case_file.model_dump()}

# Homework Endpoint
@app.post("/rogues") # Changed path from /characters
async def create_rogue_profile(rogue_profile: RogueProfile): # Expects JSON body matching RogueProfile model
    """
    Creates a new rogue profile entry based on the provided data.
    FastAPI uses the 'RogueProfile' Pydantic model to validate the request body.
    """
    print(f"Received rogue profile data: {rogue_profile}")

    # Again, normally you'd save this to a database.

    return {"message": f"Rogue profile for '{rogue_profile.alias}' created successfully.", "received_data": rogue_profile.model_dump()}


# To run this application:
# 1. Make sure you are in the 'lesson_04' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - Try the new POST /cases endpoint. Send valid JSON like:
#      {"case_name": "Fear Gas Attack", "details": "Investigate Scarecrow's latest plot", "is_open": true}
#    - Try sending invalid JSON (e.g., missing 'case_name', missing 'is_open', wrong type for 'is_open')
#      and observe the 422 validation errors FastAPI provides automatically.
#    - Try the new POST /rogues endpoint (Homework). Send valid JSON like:
#      {"alias": "Riddler", "status": "At Large", "threat_level": 7}
#      {"alias": "Catwoman", "status": "Unknown"} (threat_level defaults to 1)
#    - Try sending invalid rogue data (e.g., missing 'alias', threat_level > 10).
