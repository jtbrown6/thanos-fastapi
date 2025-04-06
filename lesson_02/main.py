# Lesson 2: The Grappling Hook - Targeting Specific Data with Path Parameters
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI

app = FastAPI()

# --- Endpoints from Lesson 1 ---

@app.get("/")
async def read_root():
    """
    The root endpoint of our API. Returns a welcome message.
    """
    return {"message": "Hello, Gotham!"}

@app.get("/status")
async def get_status():
    """
    Returns the current status of our mission in Gotham.
    """
    return {"status": "Protecting Gotham"}

# --- New Endpoints for Lesson 2 ---

# Endpoint with a string path parameter
@app.get("/locations/{location_name}") # Use location_name for Gotham places
async def scan_location(location_name: str): # Type hint ': str' validates and documents
    """
    Provides a message about scanning a specific location in Gotham.
    Receives the location name from the URL path.
    """
    print(f"Received request for location: {location_name}") # Example: logging
    # Use the path parameter in the response
    return {"message": f"Scanning location: {location_name.title()}"} # Use .title() for proper names

# Homework: Endpoint with an integer path parameter
@app.get("/gadgets/{gadget_id}") # Use gadget_id for Batman's tools
async def get_gadget(gadget_id: int): # Type hint ': int' ensures the input is an integer
    """
    Retrieves a gadget based on its ID provided in the URL path.
    FastAPI automatically validates that gadget_id is an integer.
    """
    # If you go to /gadgets/batarang, FastAPI will return a 422 error automatically!
    return {"gadget_id": gadget_id, "status": "Available"}

# Stretch Goal: Endpoint with multiple path parameters
@app.get("/rogues/{rogue_name}/cases/{case_id}") # Example: Track villains and cases
async def get_rogue_case(rogue_name: str, case_id: int):
    """
    Retrieves information about a specific case related to a rogue.
    Accepts both the rogue name (string) and case ID (integer) from the path.
    """
    return {
        "rogue": rogue_name.title(), # Capitalize rogue name
        "case_id": case_id,
        "status": "Case file found"
        }

# To run this application:
# 1. Make sure you are in the 'lesson_02' directory in your terminal
# 2. Make sure your virtual environment is activated
#    (e.g., `source ../lesson_01/venv/bin/activate` or `venv\Scripts\activate` if using Lesson 1's venv)
# 3. Run: uvicorn main:app --reload
# 4. Test endpoints in your browser or using http://127.0.0.1:8000/docs
#    - /locations/Arkham%20Asylum
#    - /gadgets/1
#    - /gadgets/batarang (observe the error)
#    - /rogues/Joker/cases/101
