# Lesson 3: Detective Mode - Querying Data & External Intel
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI
import httpx  # Library for making async HTTP requests

app = FastAPI()

# --- Endpoints from Lesson 1 & 2 (for context) ---

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
    return {"gadget_id": gadget_id, "status": "Available"}

@app.get("/rogues/{rogue_name}/cases/{case_id}")
async def get_rogue_case(rogue_name: str, case_id: int):
    return {
        "rogue": rogue_name.title(),
        "case_id": case_id,
        "status": "Case file found"
        }

# --- New Endpoints for Lesson 3 ---

# Endpoint with optional query parameters and default values
@app.get("/search-database") # More thematic path
async def search_gotham_database( # More thematic function name
    keyword: str | None = None, # Optional query parameter 'keyword'
    limit: int = 10 # Optional query parameter with a default value
    ):
    """
    Searches the Batcomputer database based on an optional keyword and limit.
    Demonstrates optional query parameters and defaults.
    """
    if keyword:
        return {"searching_for_keyword": keyword, "results_limit": limit}
    else:
        return {"message": "Provide a 'keyword' query parameter to search the database.", "results_limit": limit}

# Endpoint combining path and query parameters
@app.get("/locations/{location_name}/details") # Changed path slightly
async def get_location_details( # Changed function name
    location_name: str, # Path parameter
    min_threat_level: int = 0 # Query parameter with default, renamed for theme
    ):
    """
    Gets hypothetical details for a Gotham location, filterable by minimum threat level.
    Demonstrates combining path and query parameters.
    """
    return {
        "location": location_name.title(),
        "filter_min_threat": min_threat_level,
        "data": f"Intel report for {location_name.title()} with threat level > {min_threat_level} would go here."
        }

# Endpoint fetching data from JSONPlaceholder (External Intel - includes Stretch Goal)
@app.get("/fetch-posts") # Keeping path generic as it's external
async def fetch_external_posts(
    limit: int = 5, # Query param for our API
    user_id: int | None = None # Stretch Goal: Query param for our API
    ):
    """
    Fetches generic posts from the JSONPlaceholder API (simulating external intel).
    Allows specifying a limit and optionally filtering by user_id via query parameters.
    Demonstrates calling external APIs with httpx and basic error handling.
    """
    external_api_url = "https://jsonplaceholder.typicode.com/posts"
    
    # Build parameters for the external API call
    params = {"_limit": limit} # JSONPlaceholder uses _limit
    if user_id is not None:
        params["userId"] = user_id # JSONPlaceholder uses userId

    async with httpx.AsyncClient() as client:
        try:
            print(f"Requesting {external_api_url} with params: {params}")
            response = await client.get(external_api_url, params=params)
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            external_data = response.json()
            
            return {
                "message": f"Successfully fetched {len(external_data)} intel reports (posts) from external source",
                "source": "JSONPlaceholder API (Simulated Intel Feed)",
                "filter_params_sent": params,
                "reports": external_data # Renamed 'posts' to 'reports' for theme
            }
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            # In a real app, you'd likely return an HTTPException here
            return {"error": "Failed to fetch intel from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            # Return error info from the external API
            return {
                "error": f"External intel source returned status {exc.response.status_code}",
                "external_url": str(exc.request.url),
                "external_response": exc.response.text # Be careful about exposing external errors directly
                }

# Homework 1: Endpoint with optional query parameters
@app.get("/filter-gadgets") # Thematic path
async def filter_gadgets( # Thematic function name
    min_utility: int = 0, # Thematic parameter name
    max_utility: int | None = None # Thematic parameter name
    ):
    """
    Hypothetically filters gadgets based on utility levels.
    Demonstrates optional query parameters, one with a default.
    """
    return {
        "filtering_gadgets_by": {
            "min_utility": min_utility,
            "max_utility": max_utility if max_utility is not None else "No upper limit"
        }
    }

# Homework 2: Endpoint fetching a specific user from JSONPlaceholder (External Contact)
@app.get("/fetch-contacts/{contact_id}") # Renamed path
async def fetch_external_contact(contact_id: int): # Renamed function and parameter
    """
    Fetches a specific contact from JSONPlaceholder API (simulating an external contact database).
    Demonstrates using path parameters to construct external API URLs.
    """
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{contact_id}" # Use contact_id

    async with httpx.AsyncClient() as client:
        try:
            print(f"Requesting {external_api_url}")
            response = await client.get(external_api_url)
            response.raise_for_status() # Important for catching 404s from the external API!
            contact_data = response.json() # Renamed variable

            return {
                "message": f"Successfully fetched contact {contact_id}",
                "source": "JSONPlaceholder API (Simulated Contact DB)",
                "contact_data": contact_data # Renamed key
            }
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            return {"error": "Failed to fetch contact data from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            # This will catch the 404 if the contact_id doesn't exist on JSONPlaceholder
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            return {
                "error": f"External API returned status {exc.response.status_code} (Contact likely not found)",
                "external_url": str(exc.request.url),
                "contact_id_requested": contact_id # Renamed key
                }


# To run this application:
# 1. Make sure you are in the 'lesson_03' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install httpx: `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - /search-database?keyword=Joker&limit=3
#    - /locations/Arkham%20Asylum/details?min_threat_level=5
#    - /fetch-posts?limit=2
#    - /fetch-posts?user_id=1&limit=3 (Stretch Goal test)
#    - /filter-gadgets?min_utility=50&max_utility=100
#    - /fetch-contacts/1
#    - /fetch-contacts/999 (Test external 404 handling)
