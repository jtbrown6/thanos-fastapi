# Lesson 4: The Eye of Agamotto - Structuring Time (and Data) with Pydantic
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI
import httpx
from pydantic import BaseModel # Import Pydantic's BaseModel

app = FastAPI()

# --- Define Pydantic Models ---
# These classes define the expected structure and types for data in request bodies.

class Stone(BaseModel):
    name: str # Required string field
    description: str | None = None # Optional string field
    acquired: bool # Stretch Goal: Required boolean field

class Character(BaseModel): # Homework Model
    name: str # Required string field
    affiliation: str | None = None # Optional string field
    power_level: int = 0 # Required integer field with a default value

# --- Endpoints from Previous Lessons (for context) ---

@app.get("/")
async def read_root():
    return {"message": "Hello, Universe!"}

@app.get("/status")
async def get_status():
    return {"status": "Seeking Stones"}

@app.get("/planets/{planet_name}")
async def scan_planet(planet_name: str):
    return {"message": f"Scanning planet: {planet_name.capitalize()}"}

@app.get("/stones/{stone_id}")
async def locate_stone(stone_id: int):
    # Note: This endpoint currently just returns the ID.
    # We'll make it more useful later when we have stored data.
    return {"stone_id": stone_id, "status": "Located (hypothetically)"}

@app.get("/alliances/{ally_name}/members/{member_id}")
async def get_alliance_member(ally_name: str, member_id: int):
    return {
        "alliance": ally_name,
        "member_id": member_id,
        "status": "Found in alliance records"
        }

@app.get("/search")
async def search_reality(term: str | None = None, limit: int = 10):
    if term:
        return {"searching_for": term, "results_limit": limit}
    else:
        return {"message": "Provide a 'term' query parameter to search.", "results_limit": limit}

@app.get("/planets/{planet_name}/info")
async def get_planet_info(planet_name: str, min_power: int = 0):
    return {
        "planet": planet_name.capitalize(),
        "filter_min_power": min_power,
        "data": f"Details about {planet_name.capitalize()} with power > {min_power} would go here."
        }

@app.get("/fetch-posts")
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
                "message": f"Successfully fetched {len(external_data)} posts",
                "source": "JSONPlaceholder API",
                "filter_params_sent": params,
                "posts": external_data
            }
        # Basic error handling (omitted details for brevity in this context)
        except httpx.RequestError as exc:
            return {"error": "Failed to fetch data", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            return {"error": f"External API error: {exc.response.status_code}", "details": exc.response.text}

@app.get("/filter_stones")
async def filter_stones(min_power: int = 0, max_power: int | None = None):
    return {
        "filtering_by": {
            "min_power": min_power,
            "max_power": max_power if max_power is not None else "No upper limit"
        }
    }

@app.get("/fetch-users/{user_id}")
async def fetch_external_user(user_id: int):
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_api_url)
            response.raise_for_status()
            user_data = response.json()
            return {
                "message": f"Successfully fetched user {user_id}",
                "source": "JSONPlaceholder API",
                "user_data": user_data
            }
        # Basic error handling (omitted details for brevity in this context)
        except httpx.RequestError as exc:
            return {"error": "Failed to fetch user data", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            return {"error": f"External API error: {exc.response.status_code}", "user_id_requested": user_id}


# --- New Endpoints for Lesson 4 ---

@app.post("/stones")
async def create_stone(stone: Stone): # Expects JSON body matching the Stone model
    """
    Creates a new stone entry based on the provided data.
    FastAPI uses the 'Stone' Pydantic model to validate the request body.
    """
    print(f"Received stone data: {stone}") # Pydantic models have nice string representations
    
    # In a real application, you would typically save the validated 'stone' data
    # (e.g., stone.name, stone.description, stone.acquired) to a database.
    # For now, we just print it and return it.
    
    # Use .model_dump() (Pydantic v2+) or .dict() (Pydantic v1) to get a dictionary representation
    return {"message": f"Stone '{stone.name}' created successfully.", "received_data": stone.model_dump()}

# Homework Endpoint
@app.post("/characters")
async def create_character(character: Character): # Expects JSON body matching Character model
    """
    Creates a new character entry based on the provided data.
    FastAPI uses the 'Character' Pydantic model to validate the request body.
    """
    print(f"Received character data: {character}")
    
    # Again, normally you'd save this to a database.
    
    return {"message": f"Character '{character.name}' created successfully.", "received_data": character.model_dump()}


# To run this application:
# 1. Make sure you are in the 'lesson_04' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - Try the new POST /stones endpoint. Send valid JSON like:
#      {"name": "Time", "description": "Green and glowy", "acquired": false}
#    - Try sending invalid JSON (e.g., missing 'name', missing 'acquired', wrong type)
#      and observe the 422 validation errors.
#    - Try the new POST /characters endpoint (Homework). Send valid JSON like:
#      {"name": "Thor", "affiliation": "Avengers", "power_level": 950}
#      {"name": "Groot", "affiliation": "Guardians"} (power_level defaults to 0)
#    - Try sending invalid character data.
