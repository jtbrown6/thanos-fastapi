# Lesson 3: The Aether - Shaping Reality with Query Parameters & External APIs
# Complete code including Homework and Stretch Goal

from fastapi import FastAPI
import httpx  # Library for making async HTTP requests

app = FastAPI()

# --- Endpoints from Lesson 1 & 2 (for context) ---

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
    return {"stone_id": stone_id, "status": "Located"}

@app.get("/alliances/{ally_name}/members/{member_id}")
async def get_alliance_member(ally_name: str, member_id: int):
    return {
        "alliance": ally_name,
        "member_id": member_id,
        "status": "Found in alliance records"
        }

# --- New Endpoints for Lesson 3 ---

# Endpoint with optional query parameters and default values
@app.get("/search")
async def search_reality(
    term: str | None = None, # Optional query parameter
    limit: int = 10 # Optional query parameter with a default value
    ):
    """
    Searches based on an optional term and limit.
    Demonstrates optional query parameters and defaults.
    """
    if term:
        return {"searching_for": term, "results_limit": limit}
    else:
        return {"message": "Provide a 'term' query parameter to search.", "results_limit": limit}

# Endpoint combining path and query parameters
@app.get("/planets/{planet_name}/info")
async def get_planet_info(
    planet_name: str, # Path parameter
    min_power: int = 0 # Query parameter with default
    ):
    """
    Gets hypothetical info for a planet, filterable by minimum power level.
    Demonstrates combining path and query parameters.
    """
    return {
        "planet": planet_name.capitalize(),
        "filter_min_power": min_power,
        "data": f"Details about {planet_name.capitalize()} with power > {min_power} would go here."
        }

# Endpoint fetching data from JSONPlaceholder (includes Stretch Goal)
@app.get("/fetch-posts")
async def fetch_external_posts(
    limit: int = 5, # Query param for our API
    user_id: int | None = None # Stretch Goal: Query param for our API
    ):
    """
    Fetches posts from the JSONPlaceholder API (https://jsonplaceholder.typicode.com/posts).
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
                "message": f"Successfully fetched {len(external_data)} posts from JSONPlaceholder",
                "source": "JSONPlaceholder API",
                "filter_params_sent": params,
                "posts": external_data
            }
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            # In a real app, you'd likely return an HTTPException here
            return {"error": "Failed to fetch data from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            # Return error info from the external API
            return {
                "error": f"External API returned status {exc.response.status_code}",
                "external_url": str(exc.request.url),
                "external_response": exc.response.text # Be careful about exposing external errors directly
                }

# Homework 1: Endpoint with optional query parameters
@app.get("/filter_stones")
async def filter_stones(
    min_power: int = 0,
    max_power: int | None = None
    ):
    """
    Hypothetically filters stones based on power levels.
    Demonstrates optional query parameters, one with a default.
    """
    return {
        "filtering_by": {
            "min_power": min_power,
            "max_power": max_power if max_power is not None else "No upper limit"
        }
    }

# Homework 2: Endpoint fetching a specific user from JSONPlaceholder
@app.get("/fetch-users/{user_id}")
async def fetch_external_user(user_id: int): # Path parameter
    """
    Fetches a specific user from JSONPlaceholder API (https://jsonplaceholder.typicode.com/users/{user_id}).
    Demonstrates using path parameters to construct external API URLs.
    """
    external_api_url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    async with httpx.AsyncClient() as client:
        try:
            print(f"Requesting {external_api_url}")
            response = await client.get(external_api_url)
            response.raise_for_status() # Important for catching 404s from the external API!
            user_data = response.json()

            return {
                "message": f"Successfully fetched user {user_id}",
                "source": "JSONPlaceholder API",
                "user_data": user_data
            }
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            return {"error": "Failed to fetch user data from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            # This will catch the 404 if the user_id doesn't exist on JSONPlaceholder
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            return {
                "error": f"External API returned status {exc.response.status_code} (User likely not found)",
                "external_url": str(exc.request.url),
                "user_id_requested": user_id
                }


# To run this application:
# 1. Make sure you are in the 'lesson_03' directory
# 2. Activate virtual environment (e.g., `source ../lesson_01/venv/bin/activate`)
# 3. Install httpx: `pip install httpx`
# 4. Run: `uvicorn main:app --reload`
# 5. Test endpoints using http://127.0.0.1:8000/docs
#    - /search?term=Reality&limit=3
#    - /planets/Titan/info?min_power=100
#    - /fetch-posts?limit=2
#    - /fetch-posts?user_id=1&limit=3 (Stretch Goal test)
#    - /filter_stones?min_power=50&max_power=500
#    - /fetch-users/1
#    - /fetch-users/999 (Test external 404 handling)
