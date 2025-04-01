# Lesson 10: The Infinity Gauntlet - Assembling & Testing Your API

**Recap:** In Lesson 9, we crossed the Bifrost, learning how Middleware (like Heimdall) processes all requests/responses and how `CORSMiddleware` manages cross-origin access rules.

We've gathered all the stones (learned the core FastAPI concepts)! Now, it's time to assemble the Infinity Gauntlet itself. A gauntlet isn't just about holding the stones; it's about ensuring they work together reliably to achieve the desired effect. In software development, **Testing** is how we assemble checks for all our API features, ensuring they function correctly individually and together, allowing us to deploy with confidence – ready for the snap!

**Core Concepts:**

1.  **Why Test?** Catching bugs, preventing regressions, enabling refactoring.
2.  **Testing Framework:** Using `pytest`.
3.  **`TestClient`:** FastAPI's tool for simulating requests in tests.
4.  **Writing Tests:** Structuring test functions (`test_...`).
5.  **Making Requests:** Using `client.get()`, `client.post()`, etc.
6.  **Assertions:** Checking status codes (`response.status_code`) and response content (`response.json()`).
7.  **Testing Different Scenarios:** Success cases, error cases (404s, 400s), edge cases.

---

## 1. Why Test? The Need for Balance

Thanos sought balance, but deploying untested code leads to chaos! Testing is crucial because:

*   **Catching Bugs Early:** Find errors during development, when they are cheapest and easiest to fix, rather than in production when they impact users.
*   **Preventing Regressions:** As you add new features or change existing code (refactoring), tests ensure you haven't accidentally broken something that used to work.
*   **Enabling Refactoring:** Confidence provided by tests makes it much safer to improve code structure or performance without fear of introducing subtle bugs.
*   **Documentation:** Tests serve as executable documentation, showing how your API is intended to be used.

## 2. The Testing Framework: `pytest`

While Python has a built-in `unittest` module, `pytest` is a very popular, powerful, and less verbose third-party testing framework. FastAPI is designed to work seamlessly with `pytest`.

**Action:** Install `pytest` and `httpx` (which `TestClient` uses internally):

*   Ensure your virtual environment is active.
*   Run: `pip install pytest httpx`

## 3. Simulating Requests: `TestClient`

How can we test our API endpoints without manually running the Uvicorn server and sending requests with `curl` or `/docs` every time? FastAPI provides the `TestClient`.

You pass your FastAPI `app` object to the `TestClient`. The client then lets you make requests directly to your application *in your test code*, simulating how a real client would interact with it over HTTP, but without needing a running server.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_10`
*   Copy `main.py` from `lesson_09` into `lesson_10`: `cp lesson_09/main.py lesson_10/`
*   Create a new file for tests in the `lesson_10` directory: `touch fastapi-gauntlet-course/lesson_10/test_main.py`
*   Open `fastapi-gauntlet-course/lesson_10/test_main.py`.
*   Import `TestClient` and your FastAPI `app`:

```python
# test_main.py (in lesson_10)

from fastapi.testclient import TestClient
# Import the 'app' instance from your main application file
from main import app 

# Create a TestClient instance using your FastAPI app
client = TestClient(app) 
```

## 4. Writing Test Functions

`pytest` discovers tests by looking for files named `test_*.py` or `*_test.py` and functions within those files named `test_*`.

**Action:** Write our first simple test for the root endpoint:

```python
# test_main.py (continued)

def test_read_root():
    """ Tests the root endpoint ('/') for status code and response content. """
    # Use the client to make a GET request to "/"
    response = client.get("/") 
    
    # Assert that the HTTP status code is 200 (OK)
    assert response.status_code == 200 
    
    # Assert that the JSON response body matches the expected dictionary
    assert response.json() == {"message": "Welcome to the FastAPI Gauntlet API. Try /home for HTML view or /docs for API docs."}

```

## 5. Making Requests with the Client

The `TestClient` instance (`client`) mimics the `httpx` library's interface:

*   `client.get("/path")`
*   `client.post("/path", json={"key": "value"})`
*   `client.put("/path/{id}", json={...})`
*   `client.delete("/path/{id}")`
*   `client.request("METHOD", "/path", ...)`

You can also pass query parameters (`params={"key": "value"}`), headers (`headers={"X-API-Key": "..."}`), request body data (`json={...}`), etc., just like with `httpx`.

## 6. Assertions: Verifying the Outcome

A test isn't useful unless it verifies the result. The `assert` keyword is used for this. If the condition following `assert` is `True`, the test continues. If it's `False`, the test *fails*, and `pytest` reports the failure.

Common assertions for API tests include:

*   `assert response.status_code == EXPECTED_CODE` (e.g., 200, 201, 404, 400)
*   `assert response.json() == EXPECTED_JSON_BODY`
*   `assert "some_key" in response.json()`
*   `assert response.json()["key"] == "expected_value"`
*   `assert "Expected Text" in response.text` (for HTML responses)
*   `assert response.headers["header-name"] == "expected_value"`

## 7. Testing Different Scenarios

Good tests cover various scenarios:

*   **Success Cases:** Does the endpoint work correctly with valid input?
*   **Error Cases:** Does the endpoint return the correct HTTP error (e.g., 404, 400, 403) with the expected detail message for invalid input or non-existent resources?
*   **Edge Cases:** What happens with empty inputs, zero values, very large values, etc.?

**Action:** Add more tests to `test_main.py` covering success and failure for `GET /stones/{stone_id}`.

```python
# test_main.py (continued)

def test_locate_stone_success():
    """ Tests successfully retrieving an existing stone. """
    stone_id = 1 # Known existing stone ID
    response = client.get(f"/stones/{stone_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["stone_id"] == stone_id
    assert response_data["status"] == "Located"
    assert "details" in response_data
    assert response_data["details"]["name"] == "Space" # Check specific detail

def test_locate_stone_not_found():
    """ Tests requesting a stone ID that does not exist (expect 404). """
    stone_id = 999 # Non-existent ID
    response = client.get(f"/stones/{stone_id}")
    assert response.status_code == 404 # Check for Not Found status
    # Check if the detail message contains the ID (good practice)
    assert str(stone_id) in response.json()["detail"] 

def test_create_character_success():
    """ Tests successfully creating a new character via POST. """
    character_data = {"name": "Nebula", "affiliation": "Guardians?", "power_level": 750}
    response = client.post("/characters", json=character_data)
    assert response.status_code == 201 # Check for Created status
    response_data = response.json()
    assert response_data["name"] == character_data["name"]
    assert response_data["affiliation"] == character_data["affiliation"]
    assert response_data["power_level"] == character_data["power_level"]
    assert "id" in response_data # Check if an ID was assigned

def test_create_character_duplicate():
    """ Tests trying to create a character with a name that already exists (expect 400). """
    # First, ensure a character exists (e.g., create Nebula again or assume one exists)
    client.post("/characters", json={"name": "Existing Character", "power_level": 100}) 
    
    # Now, try to create another with the same name
    duplicate_data = {"name": "Existing Character", "power_level": 150}
    response = client.post("/characters", json=duplicate_data)
    assert response.status_code == 400 # Check for Bad Request status
    assert "already exists" in response.json()["detail"] # Check detail message

def test_home_page_loads():
    """ Tests if the HTML home page loads correctly. """
    response = client.get("/home")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] # Check content type
    assert "Knowhere Hub" in response.text # Check for expected text in HTML

def test_middleware_headers():
    """ Tests if custom middleware headers are present. """
    response = client.get("/") # Any endpoint should have middleware headers
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert "x-api-version" in response.headers
    assert response.headers["x-api-version"] == app.version # Check specific version

```

## 8. Running Your Tests

**Action:**

1.  Make sure you are in the `lesson_10` directory.
2.  Ensure your virtual environment is active.
3.  Run the command: `pytest`

`pytest` will automatically discover `test_main.py` and all functions starting with `test_`. It will run each test and report the results (e.g., `.` for pass, `F` for fail, `E` for error). If tests fail, `pytest` provides detailed output showing the assertion that failed and the values involved.

---

**Thanos Analogy Recap:**

The Infinity Gauntlet assembles the stones. Testing (`pytest` + `TestClient`) *assembles* checks for all your API features (endpoints, validation, error handling, middleware). Each `test_` function is like checking if a specific stone fits and functions correctly within the Gauntlet. Assertions (`assert`) verify the expected outcome – does reality bend as intended when you snap (`client.get/post`)? Running `pytest` is the final check before attempting the universe-altering snap (deploying to production).

**Memory Aid:**

*   `pytest`: The Gauntlet Assembler/Tester Tool
*   `TestClient(app)`: Simulator for Gauntlet Power Usage
*   `test_*.py` / `def test_*():`: Individual Stone/Feature Checks
*   `client.get/post(...)`: Simulate Using a Stone's Power
*   `assert response.status_code == ...`: Did the Power work as expected (Status)?
*   `assert response.json() == ...`: Did Reality change correctly (Content)?

---

**Homework:**

1.  Write a test function `test_create_stone_duplicate` in `test_main.py` that verifies your `POST /stones` endpoint correctly returns a `400 Bad Request` error if you try to create a stone with a name that already exists in `known_stones_db`.
2.  Write a test function `test_character_view_page` that:
    *   First, optionally POSTs a new character to `/characters` to ensure there's data.
    *   Then, makes a `GET` request to `/characters-view`.
    *   Asserts the status code is 200.
    *   Asserts that the HTML response text contains the name of the character you added (or a known character if you didn't add one).

**Stretch Goal:**

Testing endpoints that use dependencies requiring headers (like `/secure-data` from Lesson 6 which needed `X-API-Key`) can be done by passing the `headers` argument to the `TestClient` methods: `client.get("/secure-data", headers={"X-API-Key": "fake-secret-key-123"})`. Write tests for `/secure-data`:
*   One test that provides the correct header and asserts a 200 status code.
*   One test that provides an incorrect header and asserts a 403 status code.
*   One test that provides no header and asserts a 401 status code.

*(Find the complete code for this lesson in `main.py` and `test_main.py`)*

---

**Congratulations!** You have assembled the FastAPI Gauntlet, learning everything from basic setup and routing to data validation, error handling, dependencies, background tasks, templates, middleware, and finally, testing. You are now equipped to build robust and powerful APIs! The universe awaits your creations.
