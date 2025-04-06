# Lesson 10: Final Preparations - Assembling & Testing Your Batcomputer API

**Recap:** In Lesson 9, we implemented Batcave Security Protocols (Middleware) to add headers (`X-Process-Time`, `X-API-Version`) and manage Cross-Origin Resource Sharing (`CORSMiddleware`), controlling access to our API.

We've built all the components: endpoints for managing gadgets and contacts, HTML displays, background tasks handled by Alfred, security protocols... Now it's time for the **Final Preparations**. Before deploying the Batcomputer API, we need to ensure all parts work together correctly. We'll write automated tests using `pytest` and FastAPI's `TestClient` to verify our API's functionality.

**Core Concepts:**

1.  **API Testing:** Verifying that your API endpoints behave as expected.
2.  **`pytest`:** A popular and powerful Python testing framework.
3.  **`TestClient`:** FastAPI's utility (built on `httpx`) for sending simulated requests to your application *without* needing a running server.
4.  **Test Functions:** Functions starting with `test_` that `pytest` discovers and runs.
5.  **Assertions (`assert`)**: Checking if conditions are true (e.g., `assert response.status_code == 200`).
6.  **Testing Different Scenarios:** Covering success cases, error cases (like 404s, 400s), and edge cases.
7.  **Testing Request Data & Headers:** Simulating sending JSON bodies and custom headers.
8.  **Testing HTML Responses:** Checking status codes, content types, and rendered HTML content.
9.  **Test Isolation (Basic):** Using helper functions or fixtures (more advanced) to manage state between tests (like clearing the simulated database).

---

## 1. Why Test?

Automated tests act as a safety net. They:
*   Catch regressions (bugs introduced when changing code).
*   Verify functionality works as intended.
*   Provide documentation on how the API is supposed to behave.
*   Give confidence when deploying changes.

Batman wouldn't deploy a new system without rigorous testing in the Batcave simulator!

## 2. Setting Up for Testing

**Action:**

*   Create `lesson_10` directory and copy `lesson_09/main.py` into it. Also copy the `static` and `templates` directories (with their updated contents from Lesson 8) into `lesson_10`.
*   Install `pytest` and `httpx` (if not already installed):
    `pip install pytest httpx email-validator`
*   Create a new file named `lesson_10/test_main.py`.

## 3. The `TestClient`

FastAPI's `TestClient` allows you to interact with your app directly in your test code.

**Action:** In `lesson_10/test_main.py`, import `TestClient` and your `app`:

```python
# test_main.py (in lesson_10)
from fastapi.testclient import TestClient
import pytest # Optional import, pytest runs it anyway

# Import the 'app' instance from your main application file
from main import app, contacts_db # Import app and DB for cleanup helper

# Create a TestClient instance
client = TestClient(app)

# --- Test Functions Go Here ---
```

## 4. Writing Test Functions

`pytest` automatically finds and runs functions whose names start with `test_`. Inside these functions, you use the `client` to make requests and `assert` to check the results.

**Action:** Add a basic test for the root endpoint in `test_main.py`:

```python
# test_main.py (continued)

def test_read_root():
    """ Tests the root endpoint ('/') for status code and response content. """
    # Use the client to make a GET request to "/"
    response = client.get("/")
    # Assert that the HTTP status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the JSON response body matches the expected message
    assert response.json() == {"message": "Welcome to the Batcomputer API Interface. Try /batcave-display for HTML view or /docs for API docs."}

```

## 5. Testing Different Status Codes and Responses

Test both success and failure scenarios.

**Action:** Add tests for getting gadget details in `test_main.py`:

```python
# test_main.py (continued)

def test_get_gadget_details_success():
    """ Tests successfully retrieving an existing gadget (ID 1). """
    gadget_id = 1 # Batarang
    response = client.get(f"/gadgets/{gadget_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["gadget_id"] == gadget_id
    assert response_data["status"] == "Located in inventory"
    assert response_data["details"]["name"] == "Batarang"

def test_get_gadget_details_not_found():
    """ Tests requesting a gadget ID that does not exist (expect 404). """
    gadget_id = 999
    response = client.get(f"/gadgets/{gadget_id}")
    assert response.status_code == 404
    assert "Gadget with ID 999 not found" in response.json()["detail"]

```

## 6. Testing POST Requests and State Changes

When testing endpoints that modify data (like `POST /contacts`), be mindful of state. Using a global dictionary as our database means tests can interfere with each other. A simple approach is to clear the state before tests that need it. (Note: `pytest` fixtures are a much better way to handle this in real projects).

**Action:** Add tests for creating contacts, including a helper to clear the DB:

```python
# test_main.py (continued)

# Helper to clear the contacts_db via the API
def clear_contacts_db_via_api():
     delete_response = client.delete("/contacts") # Assuming DELETE /contacts exists
     assert delete_response.status_code == 204

def test_create_contact_success():
    """ Tests successfully creating a new contact via POST. """
    clear_contacts_db_via_api() # Ensure clean state
    contact_data = {"name": "Selina Kyle", "affiliation": "Complicated", "trust_level": 3}
    response = client.post("/contacts", json=contact_data) # Send JSON data
    assert response.status_code == 201 # Check for 201 Created
    response_data = response.json()
    assert response_data["name"] == contact_data["name"]
    assert "id" in response_data # Check ID was assigned

def test_create_contact_duplicate():
    """ Tests trying to create a contact with a name that already exists (expect 400). """
    clear_contacts_db_via_api()
    client.post("/contacts", json={"name": "Harvey Dent", "trust_level": 4})
    # Try creating again with same name (case-insensitive)
    duplicate_data = {"name": "harvey dent", "trust_level": 1}
    response = client.post("/contacts", json=duplicate_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

```
*(Make sure you add the `DELETE /contacts` endpoint to `main.py` for the helper function to work)*

## 7. Testing HTML Responses and Middleware

You can also test endpoints that return HTML and check if middleware added the expected headers.

**Action:** Add tests for the HTML display and middleware headers:

```python
# test_main.py (continued)

def test_batcave_display_loads():
    """ Tests if the HTML Batcave display page loads correctly. """
    response = client.get("/batcave-display")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Batcave Main Display" in response.text # Check title in HTML
    assert "Gadget Inventory:" in response.text # Check section heading

def test_middleware_headers():
    """ Tests if custom middleware headers are present. """
    response = client.get("/") # Any endpoint
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert "x-api-version" in response.headers
    assert response.headers["x-api-version"] == app.version # Check correct version

```

## 8. Running the Tests

**Action:**

1.  Make sure you are in the `lesson_10` directory in your terminal.
2.  Ensure your virtual environment is activated.
3.  Run the command: `pytest`
    *   `pytest` will automatically discover and run `test_main.py` and any functions starting with `test_`.
    *   You'll see output indicating how many tests passed or failed. Use `pytest -v` for more detail.

---

**Batman Analogy Recap:**

Final Preparations involve running diagnostics and simulations (`pytest`, `TestClient`) on the Batcomputer API. We write specific test protocols (`test_` functions) to check each function: Does the main display load (`test_batcave_display_loads`)? Can we retrieve gadget specs (`test_get_gadget_details_success`)? Does the system correctly report missing gadgets (`test_get_gadget_details_not_found`)? Does it prevent duplicate contact entries (`test_create_contact_duplicate`)? Do security headers get added (`test_middleware_headers`)? Assertions (`assert`) confirm if the results match expectations. Running `pytest` executes all these checks, ensuring the system is ready for deployment.

**Memory Aid:**

*   `pip install pytest httpx` = Get the Testing Tools
*   `from fastapi.testclient import TestClient` = Import the Simulator
*   `from main import app` = Load the System Blueprint (Your App)
*   `client = TestClient(app)` = Initialize the Simulator
*   `def test_...():` = Define a Test Protocol
*   `response = client.get("/path")` = Run a Simulation (Send Request)
*   `assert response.status_code == 200` = Check Simulation Outcome (Status Code)
*   `assert response.json() == expected_data` = Check Simulation Result (JSON Body)
*   `assert "some text" in response.text` = Check Display Content (HTML Body)
*   `assert "header" in response.headers` = Check Protocol Headers
*   `pytest` command = Run All Diagnostics

---

**Homework:**

1.  **Write `test_create_gadget_duplicate`:** Add a test function in `test_main.py` specifically for the `POST /gadgets` endpoint. It should verify that attempting to create a gadget spec with a name already present in the `gadget_inventory_db` (e.g., "Batarang") results in a `400 Bad Request` status code and an appropriate error message in the detail.
2.  **Write `test_contacts_view_page`:** Add tests for the `GET /contacts-view` endpoint.
    *   One test should ensure the page loads with a 200 status code and correct content type.
    *   Add a contact via `POST /contacts` first, then check if the contact's name appears in the HTML response of `GET /contacts-view`.
    *   Add another test that first clears the contacts DB (`clear_contacts_db_via_api`) and then checks if the "No contacts found" message appears in the HTML response of `GET /contacts-view`.

**Stretch Goal:**

Write tests for the `/gcpd-files` endpoint (or whatever endpoint you used that requires the `X-API-Key` header via the `verify_key_and_get_user` dependency).
1.  Create a test `test_gcpd_files_success` that sends the correct `X-API-Key` in the headers and asserts a 200 status code and expected success message.
2.  Create a test `test_gcpd_files_invalid_key` that sends an incorrect key and asserts a 403 status code and the specific "Invalid API Key" detail message.
3.  Create a test `test_gcpd_files_missing_key` that sends no `X-API-Key` header and asserts a 401 status code and the specific "X-API-Key header missing" detail message.
(Hint: Use `client.get("/gcpd-files", headers={"X-API-Key": "your-key-value"})`)

*(Find the complete code for this lesson, including the test file, in the repository)*

---

**Kubernetes Korner (Optional Context):**

Testing in Kubernetes often involves **Integration Tests** and **End-to-End (E2E) Tests**. While `pytest` with `TestClient` performs unit/integration tests against the application code *without* needing a full deployment, E2E tests verify the entire system deployed in a Kubernetes-like environment. Tools like `k3d` or `kind` can create local Kubernetes clusters. You might deploy your FastAPI app, database, and any other services to this local cluster and then run tests (perhaps using `pytest` with `httpx` hitting the actual deployed service endpoint, or using specialized E2E testing frameworks) to ensure all components interact correctly within the cluster environment, including networking, service discovery, and configuration.
