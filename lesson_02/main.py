# Lesson 2: The Orb - Wielding Power with Path Parameters
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI

app = FastAPI()

# --- Endpoints from Lesson 1 ---

@app.get("/")
async def read_root():
    """
    The root endpoint of our API. Returns a welcome message.
    """
    return {"message": "Hello, Universe!"}

@app.get("/status")
async def get_status():
    """
    Returns the current status of our quest.
    """
    return {"status": "Seeking Stones"}

# --- New Endpoints for Lesson 2 ---

# Endpoint with a string path parameter
@app.get("/planets/{planet_name}")
async def scan_planet(planet_name: str): # Type hint ': str' validates and documents
    """
    Provides a message about scanning a specific planet.
    Receives the planet name from the URL path.
    """
    print(f"Received request for planet: {planet_name}") # Example: logging
    # Use the path parameter in the response
    return {"message": f"Scanning planet: {planet_name.capitalize()}"}

# Homework: Endpoint with an integer path parameter
@app.get("/stones/{stone_id}")
async def locate_stone(stone_id: int): # Type hint ': int' ensures the input is an integer
    """
    Locates a stone based on its ID provided in the URL path.
    FastAPI automatically validates that stone_id is an integer.
    """
    # If you go to /stones/mind, FastAPI will return a 422 error automatically!
    return {"stone_id": stone_id, "status": "Located"}

# Stretch Goal: Endpoint with multiple path parameters
@app.get("/alliances/{ally_name}/members/{member_id}")
async def get_alliance_member(ally_name: str, member_id: int):
    """
    Retrieves information about a specific member of an alliance.
    Accepts both the alliance name (string) and member ID (integer) from the path.
    """
    return {
        "alliance": ally_name,
        "member_id": member_id,
        "status": "Found in alliance records"
        }

# To run this application:
# 1. Make sure you are in the 'lesson_02' directory in your terminal
# 2. Make sure your virtual environment is activated
#    (e.g., `source ../lesson_01/venv/bin/activate` or `venv\Scripts\activate` if using Lesson 1's venv)
# 3. Run: uvicorn main:app --reload
# 4. Test endpoints in your browser or using http://127.0.0.1:8000/docs
#    - /planets/Xandar
#    - /stones/1
#    - /stones/mind (observe the error)
#    - /alliances/Avengers/members/3
