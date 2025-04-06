# Lesson 10: The Infinity Gauntlet - Assembling & Testing Your API
# Test file using pytest and TestClient

from fastapi.testclient import TestClient
import pytest # pytest is automatically used when running 'pytest' command

# Import the 'app' instance from your main application file (main.py)
# Ensure main.py is in the same directory or accessible via Python path.
from main import app, contacts_db # Import app and the contacts_db for cleanup

# Create a TestClient instance using your FastAPI app
# This client will simulate HTTP requests to your app without needing a running server.
client = TestClient(app)

# --- Test Functions ---
# pytest discovers functions starting with 'test_'

def test_read_root():
    """ Tests the root endpoint ('/') for status code and response content. """
    response = client.get("/")
    assert response.status_code == 200
    # Check the specific message from the updated main.py
    assert response.json() == {"message": "Welcome to the Batcomputer API Interface. Try /batcave-display for HTML view or /docs for API docs."}

def test_get_gadget_details_success(): # Renamed function
    """ Tests successfully retrieving an existing gadget (ID 1). """
    gadget_id = 1 # Known existing gadget ID from gadget_inventory_db
    response = client.get(f"/gadgets/{gadget_id}") # Updated path
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["gadget_id"] == gadget_id
    assert response_data["status"] == "Located in inventory" # Updated status message
    assert "details" in response_data
    assert response_data["details"]["name"] == "Batarang" # Verify specific gadget data

def test_get_gadget_details_not_found(): # Renamed function
    """ Tests requesting a gadget ID that does not exist (expect 404). """
    gadget_id = 999 # Non-existent ID
    response = client.get(f"/gadgets/{gadget_id}") # Updated path
    assert response.status_code == 404 # Check for Not Found status
    assert "detail" in response.json() # FastAPI error responses have 'detail'
    assert str(gadget_id) in response.json()["detail"] # Check if detail mentions the ID
    assert "Gadget" in response.json()["detail"] # Check for thematic error message

# --- Tests for Contact Creation ---

# Helper to ensure clean state for contact tests if needed
def clear_contacts_db_via_api(): # Renamed helper
     # It's often better to use pytest fixtures for setup/teardown,
     # but calling an endpoint is simpler for this example.
     delete_response = client.delete("/contacts") # Updated path
     assert delete_response.status_code == 204 # No Content

def test_create_contact_success(): # Renamed function
    """ Tests successfully creating a new contact via POST. """
    clear_contacts_db_via_api() # Start with a clean slate
    contact_data = {"name": "Alfred Pennyworth", "affiliation": "Wayne Enterprises", "trust_level": 5} # Updated data structure
    response = client.post("/contacts", json=contact_data) # Updated path
    assert response.status_code == 201 # Check for Created status
    response_data = response.json()
    assert response_data["name"] == contact_data["name"]
    assert response_data["affiliation"] == contact_data["affiliation"]
    assert response_data["trust_level"] == contact_data["trust_level"] # Check updated field
    assert "id" in response_data # Check if an ID was assigned (should be 1 after clearing)
    assert response_data["id"] == 1

def test_create_contact_duplicate(): # Renamed function
    """ Tests trying to create a contact with a name that already exists (expect 400). """
    clear_contacts_db_via_api()
    # First, create a contact
    client.post("/contacts", json={"name": "James Gordon", "affiliation": "GCPD", "trust_level": 5}) # Updated path and data

    # Now, try to create another with the same name (case-insensitive check in main.py)
    duplicate_data = {"name": "james gordon", "trust_level": 4} # Updated data
    response = client.post("/contacts", json=duplicate_data) # Updated path
    assert response.status_code == 400 # Check for Bad Request status
    assert "already exists" in response.json()["detail"]
    assert "Contact" in response.json()["detail"] # Check for thematic error message

# --- Homework Test 1 (Updated for Gadgets) ---
def test_create_gadget_duplicate(): # Renamed function
    """ Tests POST /gadgets returns 400 if gadget name exists in gadget_inventory_db. """
    # Try to create a gadget spec with a name that's already in the fixed gadget_inventory_db
    duplicate_gadget_data = {"name": "Batarang", "description": "Another one?", "in_stock": False} # Updated data
    response = client.post("/gadgets", json=duplicate_gadget_data) # Updated path
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
    assert "'Batarang'" in response.json()["detail"] # Check if name is mentioned
    assert "Gadget" in response.json()["detail"] # Check for thematic error message

# --- Tests for HTML Pages ---

def test_batcave_display_loads(): # Renamed function
    """ Tests if the HTML Batcave display page loads correctly and contains expected text. """
    response = client.get("/batcave-display") # Updated path
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] # Check content type
    # Check for text content that should be rendered by Jinja2
    assert "Batcave Main Display" in response.text # Updated title
    assert "Welcome to the Batcave" in response.text # Updated heading
    assert "Gadget Inventory:" in response.text # Updated section
    assert "Batarang" in response.text # Check if gadget data is rendered

# --- Homework Test 2 (Updated for Contacts) ---
def test_contacts_view_page(): # Renamed function
    """ Tests the GET /contacts-view HTML page. """
    clear_contacts_db_via_api() # Use updated helper
    # Add a contact so the list isn't empty
    contact_name = "Lucius Fox"
    client.post("/contacts", json={"name": contact_name, "affiliation": "Wayne Enterprises"}) # Updated path and data

    # Request the HTML page
    response = client.get("/contacts-view") # Updated path
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check if the contact name appears in the rendered HTML
    assert contact_name in response.text
    assert "Registered Contacts" in response.text # Check updated heading

def test_contacts_view_page_empty(): # Renamed function
    """ Tests the GET /contacts-view page when no contacts exist. """
    clear_contacts_db_via_api() # Ensure DB is empty using updated helper
    response = client.get("/contacts-view") # Updated path
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "No contacts found" in response.text # Check the updated 'else' block message

# --- Test for Middleware ---

def test_middleware_headers():
    """ Tests if custom middleware headers (X-Process-Time, X-API-Version) are present. """
    response = client.get("/") # Any endpoint should have middleware headers
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert "x-api-version" in response.headers
    # Check the specific version defined in main.py's app instance
    assert response.headers["x-api-version"] == app.version

# --- Stretch Goal Tests for /gcpd-files (Updated Path/Key) ---

def test_gcpd_files_success(): # Renamed function
    """ Tests /gcpd-files with the correct API key header. """
    headers = {"X-API-Key": "gcpd-secret-key-789"} # Use updated key
    response = client.get("/gcpd-files", headers=headers) # Updated path
    assert response.status_code == 200
    assert response.json()["message"] == "Access granted to secure GCPD files." # Updated message
    assert "gcpd_officer_jim" in response.json()["accessed_by"]["user_id"] # Updated user

def test_gcpd_files_invalid_key(): # Renamed function
    """ Tests /gcpd-files with an incorrect API key header (expect 403). """
    headers = {"X-API-Key": "arkham-key"} # Incorrect key
    response = client.get("/gcpd-files", headers=headers) # Updated path
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Invalid API Key provided (Access Denied)" # Updated message

def test_gcpd_files_missing_key(): # Renamed function
    """ Tests /gcpd-files with no API key header (expect 401). """
    response = client.get("/gcpd-files") # Updated path, no headers argument passed
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "X-API-Key header missing (Authentication required)" # Updated message


# To run these tests:
# 1. Make sure you are in the 'lesson_10' directory.
# 2. Ensure your virtual environment is activated.
# 3. Install pytest and httpx: `pip install pytest httpx`
# 4. Run the command: `pytest`
#    (or `pytest -v` for more verbose output)
