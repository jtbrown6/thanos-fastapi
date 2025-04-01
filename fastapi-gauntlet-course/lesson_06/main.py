# Lesson 6: The Mind Stone's Influence - Dependency Injection
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI, HTTPException, Depends, Header # Import Depends and Header
import httpx
from pydantic import BaseModel
from typing import Annotated # Needed for newer FastAPI/Pydantic type hinting with Depends

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

# --- Simulate a Database (from Lesson 5) ---
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

# Dependency to get API Key from header
async def get_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    """ Dependency to extract an API key from the X-API-Key header. """
    print(f"API Key dependency checking header: {x_api_key}")
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    return x_api_key

APIKeyDep = Annotated[str, Depends(get_api_key)]

# Dependency that depends on another dependency
async def verify_key_and_get_user(api_key: APIKeyDep): # Depends on get_api_key implicitly via APIKeyDep
    """ Dependency that depends on get_api_key and verifies it. """
    print(f"Verifying API key: {api_key}")
    if api_key != "fake-secret-key-123": # Simulate checking the key
        raise HTTPException(status_code=403, detail="Invalid API Key provided")
    # Simulate fetching user based on key
    user_data = {"user_id": "user_for_" + api_key, "permissions": ["read"]}
    print(f"API Key verified, returning user data: {user_data}")
    return user_data

VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]

# --- Homework/Stretch Goal Dependencies ---

# Homework Dependency 1 & 3
async def get_current_user():
    """ Simulates fetching user data. Raises error if user is inactive. """
    # Simulate fetching user data
    user_data = {"username": "thanos", "email": "thanos@titan.net", "is_active": True}
    # user_data = {"username": "ebony_maw", "email": "maw@blackorder.net", "is_active": False} # Test inactive case

    print(f"Dependency 'get_current_user' returning: {user_data}")
    if not user_data["is_active"]:
         raise HTTPException(status_code=400, detail="Inactive user") # Homework 3 check
    return user_data

CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# Stretch Goal Dependency
async def verify_admin_user(current_user: CurrentUserDep): # Depends on get_current_user
    """ Verifies if the current user is the admin ('thanos'). """
    print(f"Dependency 'verify_admin_user' checking user: {current_user['username']}")
    if current_user["username"] != "thanos":
        raise HTTPException(status_code=403, detail="Admin privileges required. You shall not pass!")
    print("Admin user verified.")
    return current_user # Pass the user data along if needed

AdminUserDep = Annotated[dict, Depends(verify_admin_user)]


# --- Endpoints from Previous Lessons (mostly unchanged) ---
# (Keeping a few for context, removing others for brevity)

@app.get("/")
async def read_root():
    return {"message": "Hello, Universe!"}

@app.get("/stones/{stone_id}")
async def locate_stone(stone_id: int):
    if stone_id not in known_stones_db:
        raise HTTPException(status_code=404, detail=f"Stone with ID {stone_id} not found.")
    return {"stone_id": stone_id, "status": "Located", "details": known_stones_db[stone_id]}

@app.post("/stones")
async def create_stone(stone: Stone):
    for existing_stone in known_stones_db.values():
        if existing_stone["name"].lower() == stone.name.lower():
            raise HTTPException(status_code=400, detail=f"Stone named '{stone.name}' already exists.")
    return {"message": f"Stone '{stone.name}' would be created (simulation).", "received_data": stone.model_dump()}

@app.post("/characters", status_code=201)
async def create_character(character: Character):
    global next_character_id
    for char_data in characters_db.values():
        if char_data["name"].lower() == character.name.lower():
            raise HTTPException(status_code=400, detail=f"Character named '{character.name}' already exists.")
    new_id = next_character_id
    characters_db[new_id] = character.model_dump()
    characters_db[new_id]["id"] = new_id
    next_character_id += 1
    return characters_db[new_id]

# --- New Endpoints for Lesson 6 ---

@app.get("/items/")
async def read_items(commons: CommonsDep): # Use the dependency
    """ Reads items using common pagination parameters from DI. """
    print(f"Endpoint '/items/' using commons: {commons}")
    all_item_ids = list(range(1000))
    start = commons['skip']
    end = start + commons['limit']
    paginated_items = all_item_ids[start:end]
    return {"skip": commons['skip'], "limit": commons['limit'], "items": paginated_items}

@app.get("/users/")
async def read_users(commons: CommonsDep): # Reuse the same dependency
    """ Reads users using common pagination parameters from DI. """
    print(f"Endpoint '/users/' using commons: {commons}")
    all_user_ids = ["User_A", "User_B", "User_C", "User_D", "User_E"]
    start = commons['skip']
    end = start + commons['limit']
    paginated_users = all_user_ids[start:end]
    return {"skip": commons['skip'], "limit": commons['limit'], "users": paginated_users}

@app.get("/data-from-db")
async def get_data(db: DBSessionDep): # Use the yielding dependency
    """ Reads data using a dependency-managed DB session. """
    print(f"--- Endpoint using DB session ID: {db.get('id')} ---")
    db["data"]["item1"] = "value1"
    return {"message": "Data accessed using DB session", "session_details": db}

@app.get("/data-from-db-error")
async def get_data_error(db: DBSessionDep): # Use the yielding dependency
    """ Simulates an error occurring while using the DB session. """
    print(f"--- Endpoint (error case) using DB session ID: {db.get('id')} ---")
    db["data"]["item1"] = "value1"
    raise HTTPException(status_code=500, detail="Something went wrong in the endpoint!")
    # The 'finally' block in get_db_session will still run.

@app.get("/secure-data")
async def read_secure_data(current_user: VerifiedUserDep): # Use the chained dependency
     """ Accesses secure data, requiring a valid API key via dependencies. """
     print(f"Endpoint accessing data for user: {current_user.get('user_id')}")
     return {"message": "This is secure data.", "accessed_by": current_user}

# --- Homework/Stretch Goal Endpoints ---

# Homework Endpoint 2
@app.get("/users/me")
async def read_current_user(current_user: CurrentUserDep): # Use the homework dependency
    """ Gets the current logged-in user's data (simulated). """
    print(f"Endpoint '/users/me' returning user: {current_user}")
    return current_user

# Stretch Goal Endpoint
@app.get("/admin/panel")
async def read_admin_panel(admin_user: AdminUserDep): # Use the stretch goal dependency
    """ Accesses the admin panel, requires 'thanos' user via dependencies. """
    print(f"Endpoint '/admin/panel' accessed by: {admin_user['username']}")
    return {"message": f"Welcome to the Admin Panel, Lord {admin_user['username']}!"}


# To run this application:
# 1. Make sure you are in the 'lesson_06' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install dependencies if needed: `pip install "fastapi[all]"` and `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - /items/?skip=5&limit=10
#    - /users/?limit=2
#    - /data-from-db (check terminal for open/close messages)
#    - /data-from-db-error (check terminal for open/close messages despite error)
#    - /secure-data (Try it out, add header X-API-Key: fake-secret-key-123)
#    - /secure-data (Try with wrong/missing X-API-Key header)
#    - /users/me (Homework)
#    - /admin/panel (Stretch Goal - should work if get_current_user returns 'thanos')
#    - (Optional: Modify get_current_user to return a different username and test /admin/panel again - should fail with 403)
#    - (Optional: Modify get_current_user to set is_active=False and test /users/me - should fail with 400)
