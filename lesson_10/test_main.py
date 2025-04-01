# Lesson 10: The Infinity Gauntlet - Assembling & Testing Your API
# Test file using pytest and TestClient

from fastapi.testclient import TestClient
import pytest # pytest is automatically used when running 'pytest' command

# Import the 'app' instance from your main application file (main.py)
# Ensure main.py is in the same directory or accessible via Python path.
from main import app, characters_db # Import app and potentially the db for cleanup

# Create a TestClient instance using your FastAPI app
# This client will simulate HTTP requests to your app without needing a running server.
client = TestClient(app)

# --- Test Functions ---
# pytest discovers functions starting with 'test_'

def test_read_root():
    """ Tests the root endpoint ('/') for status code and response content. """
    response = client.get("/")
    assert response.status_code == 200
    # Check the specific message from Lesson 10's main.py
    assert response.json() == {"message": "Welcome to the FastAPI Gauntlet API. Try /home for HTML view or /docs for API docs."}

def test_locate_stone_success():
    """ Tests successfully retrieving an existing stone (ID 1). """
    stone_id = 1 # Known existing stone ID from known_stones_db
    response = client.get(f"/stones/{stone_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["stone_id"] == stone_id
    assert response_data["status"] == "Located"
    assert "details" in response_data
    assert response_data["details"]["name"] == "Space" # Verify specific data

def test_locate_stone_not_found():
    """ Tests requesting a stone ID that does not exist (expect 404). """
    stone_id = 999 # Non-existent ID
    response = client.get(f"/stones/{stone_id}")
    assert response.status_code == 404 # Check for Not Found status
    assert "detail" in response.json() # FastAPI error responses have 'detail'
    assert str(stone_id) in response.json()["detail"] # Check if detail mentions the ID

# --- Tests for Character Creation ---

# Helper to ensure clean state for character tests if needed
def clear_character_db_via_api():
     # It's often better to use pytest fixtures for setup/teardown,
     # but calling an endpoint is simpler for this example.
     delete_response = client.delete("/characters")
     assert delete_response.status_code == 204 # No Content

def test_create_character_success():
    """ Tests successfully creating a new character via POST. """
    clear_character_db_via_api() # Start with a clean slate
    character_data = {"name": "Nebula", "affiliation": "Guardians?", "power_level": 750}
    response = client.post("/characters", json=character_data)
    assert response.status_code == 201 # Check for Created status
    response_data = response.json()
    assert response_data["name"] == character_data["name"]
    assert response_data["affiliation"] == character_data["affiliation"]
    assert response_data["power_level"] == character_data["power_level"]
    assert "id" in response_data # Check if an ID was assigned (should be 1 after clearing)
    assert response_data["id"] == 1

def test_create_character_duplicate():
    """ Tests trying to create a character with a name that already exists (expect 400). """
    clear_character_db_via_api()
    # First, create a character
    client.post("/characters", json={"name": "Gamora", "affiliation": "Guardians", "power_level": 800})

    # Now, try to create another with the same name (case-insensitive check in main.py)
    duplicate_data = {"name": "gamora", "power_level": 801}
    response = client.post("/characters", json=duplicate_data)
    assert response.status_code == 400 # Check for Bad Request status
    assert "already exists" in response.json()["detail"]

# --- Homework Test 1 ---
def test_create_stone_duplicate():
    """ Tests POST /stones returns 400 if stone name exists in known_stones_db. """
    # Try to create a stone with a name that's already in the fixed known_stones_db
    duplicate_stone_data = {"name": "Time", "description": "Another Time stone?", "acquired": False}
    response = client.post("/stones", json=duplicate_stone_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
    assert "'Time'" in response.json()["detail"] # Check if name is mentioned

# --- Tests for HTML Pages ---

def test_home_page_loads():
    """ Tests if the HTML home page loads correctly and contains expected text. """
    response = client.get("/home")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] # Check content type
    # Check for text content that should be rendered by Jinja2
    assert "Knowhere Hub" in response.text
    assert "Welcome to the Collector's Archive!" in response.text
    assert "Known Stones:" in response.text
    assert "Space" in response.text # Check if stone data is rendered

# --- Homework Test 2 ---
def test_character_view_page():
    """ Tests the GET /characters-view HTML page. """
    clear_character_db_via_api()
    # Add a character so the list isn't empty
    char_name = "Rocket"
    client.post("/characters", json={"name": char_name, "affiliation": "Guardians"})

    # Request the HTML page
    response = client.get("/characters-view")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check if the character name appears in the rendered HTML
    assert char_name in response.text
    assert "Registered Characters" in response.text # Check heading

def test_character_view_page_empty():
    """ Tests the GET /characters-view page when no characters exist. """
    clear_character_db_via_api() # Ensure DB is empty
    response = client.get("/characters-view")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "No characters found" in response.text # Check the 'else' block message

# --- Test for Middleware ---

def test_middleware_headers():
    """ Tests if custom middleware headers (X-Process-Time, X-API-Version) are present. """
    response = client.get("/") # Any endpoint should have middleware headers
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert "x-api-version" in response.headers
    # Check the specific version defined in main.py's app instance
    assert response.headers["x-api-version"] == app.version

# --- Stretch Goal Tests for /secure-data ---

def test_secure_data_success():
    """ Tests /secure-data with the correct API key header. """
    headers = {"X-API-Key": "fake-secret-key-123"}
    response = client.get("/secure-data", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "This is secure data."
    assert "user_for_fake-secret-key-123" in response.json()["accessed_by"]["user_id"]

def test_secure_data_invalid_key():
    """ Tests /secure-data with an incorrect API key header (expect 403). """
    headers = {"X-API-Key": "wrong-key"}
    response = client.get("/secure-data", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Invalid API Key provided"

def test_secure_data_missing_key():
    """ Tests /secure-data with no API key header (expect 401). """
    response = client.get("/secure-data") # No headers argument passed
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "X-API-Key header missing"


# To run these tests:
# 1. Make sure you are in the 'lesson_10' directory.
# 2. Ensure your virtual environment is activated.
# 3. Install pytest and httpx: `pip install pytest httpx`
# 4. Run the command: `pytest`
#    (or `pytest -v` for more verbose output)
