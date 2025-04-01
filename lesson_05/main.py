# Lesson 5: Vormir's Sacrifice - Handling Errors Gracefully with HTTPException
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException # Import HTTPException
import httpx
from pydantic import BaseModel

app = FastAPI()

# --- Define Pydantic Models (from Lesson 4) ---

class Stone(BaseModel):
    name: str
    description: str | None = None
    acquired: bool

class Character(BaseModel):
    name: str
    affiliation: str | None = None
    power_level: int = 0

# --- Simulate a Database ---
# In a real app, this data would live in a database.
# We use a dictionary here for simplicity.
known_stones_db = {
    1: {"name": "Space", "location": "Tesseract", "color": "Blue", "acquired": True},
    2: {"name": "Mind", "location": "Scepter/Vision", "color": "Yellow", "acquired": True},
    3: {"name": "Reality", "location": "Aether", "color": "Red", "acquired": True},
    4: {"name": "Power", "location": "Orb/Gauntlet", "color": "Purple", "acquired": True},
    5: {"name": "Time", "location": "Eye of Agamotto", "color": "Green", "acquired": True},
    6: {"name": "Soul", "location": "Vormir/Gauntlet", "color": "Orange", "acquired": True}
}

# We'll store created characters here (again, simulating a DB)
characters_db = {}
next_character_id = 1

# --- Endpoints from Previous Lessons (some modified for Lesson 5) ---

@app.get("/")
async def read_root():
    return {"message": "Hello, Universe!"}

@app.get("/status")
async def get_status():
    # Let's make status dynamic based on our DB
    acquired_count = sum(1 for stone in known_stones_db.values() if stone.get("acquired"))
    status = "All stones acquired!" if acquired_count == 6 else f"Seeking {6 - acquired_count} more stones..."
    return {"status": status, "stones_acquired": acquired_count}

@app.get("/planets/{planet_name}")
async def scan_planet(planet_name: str):
    return {"message": f"Scanning planet: {planet_name.capitalize()}"}

# --- Modified for Lesson 5: GET /stones/{stone_id} ---
@app.get("/stones/{stone_id}")
async def locate_stone(stone_id: int):
    """
    Retrieves details for a specific stone by its ID.
    Returns a 404 error if the stone ID is not found in known_stones_db.
    """
    if stone_id not in known_stones_db:
        # Raise 404 Not Found error if ID doesn't exist
        raise HTTPException(
            status_code=404,
            detail=f"Sacrifice failed! Stone with ID {stone_id} not found on Vormir (or anywhere else)."
        )
    # If found, return the data
    stone_data = known_stones_db[stone_id]
    return {"stone_id": stone_id, "status": "Located", "details": stone_data}

@app.get("/alliances/{ally_name}/members/{member_id}")
async def get_alliance_member(ally_name: str, member_id: int):
    # This remains hypothetical
    return {
        "alliance": ally_name,
        "member_id": member_id,
        "status": "Found in alliance records"
        }

@app.get("/search")
async def search_reality(term: str | None = None, limit: int = 10):
    if term:
        # Hypothetical search logic could go here
        return {"searching_for": term, "results_limit": limit, "results": []}
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
        except httpx.RequestError as exc:
             raise HTTPException(status_code=503, detail=f"External API request failed: {exc}")
        except httpx.HTTPStatusError as exc:
             raise HTTPException(status_code=exc.response.status_code, detail=f"External API error: {exc.response.text}")

@app.get("/filter_stones")
async def filter_stones(min_power: int = 0, max_power: int | None = None):
    # Hypothetical filtering
    filtered = {sid: data for sid, data in known_stones_db.items() if data.get('power', 0) >= min_power and (max_power is None or data.get('power', 0) <= max_power)}
    return {
        "filtering_by": {
            "min_power": min_power,
            "max_power": max_power if max_power is not None else "No upper limit"
        },
        "results": filtered
    }

# --- Modified for Lesson 5 Stretch Goal: GET /fetch-users/{user_id} ---
@app.get("/fetch-users/{user_id}")
async def fetch_external_user(user_id: int):
    """
    Fetches a specific user from JSONPlaceholder API.
    Raises 404 if the user is not found in the external source.
    """
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_api_url)
            response.raise_for_status() # Raises exception for 4xx/5xx status codes
            user_data = response.json()
            return {
                "message": f"Successfully fetched user {user_id}",
                "source": "JSONPlaceholder API",
                "user_data": user_data
            }
        except httpx.RequestError as exc:
            # Error connecting to the external service
            raise HTTPException(status_code=503, detail=f"External API request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            # Handle specific errors from the external API
            if exc.response.status_code == 404:
                # If external API gives 404, we raise our own 404
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found in external source.")
            else:
                # For other errors, maybe return a generic server error or relay status
                raise HTTPException(status_code=502, # Bad Gateway might be appropriate
                                    detail=f"External API returned status {exc.response.status_code}: {exc.response.text}")


# --- Modified for Lesson 5 Homework: POST /stones ---
@app.post("/stones")
async def create_stone(stone: Stone):
    """
    Creates a new stone entry.
    Raises 400 error if a stone with the same name already exists.
    """
    # Homework: Check if stone name already exists (case-insensitive check)
    for existing_stone in known_stones_db.values():
        if existing_stone["name"].lower() == stone.name.lower():
            raise HTTPException(
                status_code=400, # Bad Request
                detail=f"A stone named '{stone.name}' already exists. Choose a different name."
            )

    # If name is unique, proceed (in real app, generate ID and save to DB)
    print(f"Received stone data: {stone}")
    # Simulate adding to DB (but known_stones_db is fixed for now)
    # In a real app: new_id = db.insert(stone); return db.get(new_id)
    return {"message": f"Stone '{stone.name}' would be created (simulation).", "received_data": stone.model_dump()}

# --- Modified for Lesson 5: POST /characters ---
@app.post("/characters", status_code=201) # Use 201 Created status code
async def create_character(character: Character):
    """
    Creates a new character entry.
    (Simulates adding to an in-memory dictionary)
    """
    global next_character_id # Allow modification of the global variable
    # Basic check for duplicate name (could be more robust)
    for char_data in characters_db.values():
        if char_data["name"].lower() == character.name.lower():
            raise HTTPException(status_code=400, detail=f"Character named '{character.name}' already exists.")

    # Assign an ID and store in our simulated DB
    new_id = next_character_id
    characters_db[new_id] = character.model_dump()
    characters_db[new_id]["id"] = new_id # Add the ID to the stored data
    next_character_id += 1

    print(f"Created character: {characters_db[new_id]}")
    # Return the created character data along with its new ID
    return characters_db[new_id]


# To run this application:
# 1. Make sure you are in the 'lesson_05' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - GET /stones/1 (Success 200)
#    - GET /stones/99 (Failure 404)
#    - POST /stones with body {"name": "Imagination", "description": "Not canon", "acquired": false} (Success 200)
#    - POST /stones with body {"name": "Time", "description": "Duplicate", "acquired": true} (Failure 400)
#    - GET /fetch-users/1 (Success 200)
#    - GET /fetch-users/999 (Failure 404 - from our API via Stretch Goal)
#    - POST /characters with body {"name": "Gamora", "affiliation": "Guardians", "power_level": 800} (Success 201)
#    - POST /characters with body {"name": "Gamora", "affiliation": "Also Guardians"} (Failure 400)
