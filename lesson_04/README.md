# Lesson 4: The Utility Belt - Structuring Data with Pydantic Models

**Recap:** In Lesson 3, we activated Detective Mode (Query Parameters) to filter data (`?keyword=...`) and learned to access external intel (`httpx`) like Oracle's network.

Now, we focus on the **Utility Belt**. It doesn't just hold random items; each gadget has a specific design and purpose. Similarly, when our API *receives* data (e.g., when creating a new case file or adding a rogue profile), we need a way to define the expected structure and data types. **Pydantic Models** are FastAPI's built-in way to declare these data "blueprints."

**Core Concepts:**

1.  **Request Body:** Data sent by the client in the body of requests (typically POST, PUT, PATCH).
2.  **Pydantic:** A data validation and parsing library integrated into FastAPI.
3.  **`BaseModel`:** The base class for creating Pydantic models.
4.  **Defining Models:** Declaring data fields with type hints within a class inheriting from `BaseModel`.
5.  **Using Models in Endpoints:** Type hinting function parameters with the Pydantic model to automatically handle request body parsing and validation.
6.  **Automatic Validation & Error Handling:** FastAPI uses Pydantic models to automatically validate incoming data and return detailed errors (HTTP 422) if it doesn't match the structure.
7.  **Automatic Documentation:** `/docs` uses Pydantic models to show the expected request body structure.

---

## 1. Why Structure Incoming Data?

So far, our endpoints mostly *returned* data (`GET` requests). But often, APIs need to *receive* data to create or update resources. For example, creating a new case file requires information like the case name, details, and status.

We need to tell FastAPI: "When a client sends data to create a case file, it *must* include a `case_name` (string) and an `is_open` status (boolean), and it *can optionally* include `details` (string)."

## 2. Pydantic `BaseModel`: The Blueprint

Pydantic provides the `BaseModel` class. We create our own classes that inherit from it, defining the fields and their types.

**Action:**

*   Create `lesson_04` directory and copy `lesson_03/main.py` into it.
*   Open `lesson_04/main.py`.
*   Import `BaseModel` and `Field` from `pydantic`.
*   Define the `CaseFile` model near the top of the file:

```python
# main.py (in lesson_04)
from fastapi import FastAPI
import httpx
from pydantic import BaseModel, Field # Import BaseModel and Field

app = FastAPI()

# --- Define Pydantic Models (Data Blueprints) ---

class CaseFile(BaseModel):
    # Field(..., description="...") makes the field required and adds description to docs
    case_name: str = Field(..., description="The unique name or identifier for the case.")
    # Field(None, ...) makes the field optional
    details: str | None = Field(None, description="Optional details or summary of the case.")
    is_open: bool = Field(..., description="Whether the case is currently active/open.")

# ... (rest of the code from lesson 3 for now) ...
```

*   `CaseFile` inherits from `BaseModel`.
*   `case_name: str = Field(...)`: Defines a required field named `case_name` that must be a string. `...` indicates it's required.
*   `details: str | None = Field(None, ...)`: Defines an optional field `details`. It can be a string or `None`. `None` as the first argument to `Field` makes it optional.
*   `is_open: bool = Field(...)`: Defines a required field `is_open` that must be a boolean.
*   `Field` allows adding extra information like descriptions, validation rules (see Homework), etc.

## 3. Using Models in Path Operations (POST Requests)

Now, let's create an endpoint that *receives* data matching the `CaseFile` structure. We typically use HTTP `POST` requests for creating new resources.

**Action:** Add this endpoint to `lesson_04/main.py`:

```python
# main.py (in lesson_04)
# ... (after previous endpoints) ...

# --- New Endpoints for Lesson 4: Receiving Structured Data ---

@app.post("/cases") # Use POST for creating resources
async def create_case(case_file: CaseFile): # Type hint the parameter with the Pydantic model
    """
    Creates a new case file entry based on the provided data.
    FastAPI uses the 'CaseFile' Pydantic model to validate the request body automatically.
    """
    # Because we type-hinted 'case_file' with 'CaseFile', FastAPI automatically:
    # 1. Reads the JSON body of the incoming POST request.
    # 2. Validates if the JSON matches the CaseFile structure (required fields, types).
    # 3. If valid, converts the JSON into a CaseFile object and passes it here.
    # 4. If invalid, automatically sends back an HTTP 422 error with details.

    print(f"Received case file data: {case_file}")

    # You can access the data like attributes: case_file.case_name, case_file.details
    # In a real app, save this data to a database.

    # Return a confirmation message, including the received data
    # Use .model_dump() (Pydantic v2+) or .dict() (Pydantic v1) for a dictionary representation
    return {"message": f"Case File '{case_file.case_name}' created successfully.", "received_data": case_file.model_dump()}

```

By simply type hinting `case_file: CaseFile`, FastAPI handles the request body parsing and validation for us!

## 4. Testing Request Body Validation

The real power comes from automatic validation.

**Action:**

1.  Ensure you are in the `lesson_04` directory.
2.  Activate your virtual environment.
3.  Run the server: `uvicorn main:app --reload`
4.  Go to `http://127.0.0.1:8000/docs`.
5.  Find the new `POST /cases` endpoint. Expand it.
6.  Notice the "Request body" section in `/docs`. It shows the exact JSON structure expected, based on our `CaseFile` model! This is automatic documentation generation.
7.  Click "**Try it out**".
8.  Edit the example Request body JSON:
    *   **Valid:** Send something like:
        ```json
        {
          "case_name": "Bank Heist at Gotham National",
          "details": "Investigate Joker's involvement.",
          "is_open": true
        }
        ```
        You should get a `200 OK` response. Check the terminal where `uvicorn` is running; you'll see the printed `CaseFile` object.
    *   **Invalid (Missing Required Field):** Remove the `"is_open": true` line and click "Execute". You should get a `422 Unprocessable Entity` error response. The response body will detail exactly which field is missing.
    *   **Invalid (Wrong Type):** Change `"is_open": true` to `"is_open": "maybe"` and click "Execute". You'll get another `422` error, indicating that "maybe" is not a valid boolean.

FastAPI and Pydantic handle all this validation automatically, saving you immense effort and making your API robust.

---

**Batman Analogy Recap:**

The Utility Belt (`Pydantic Models`) provides blueprints (`BaseModel` classes) for data structures, like case files or rogue profiles. When receiving data (`POST /cases`), FastAPI uses these blueprints (`case_file: CaseFile`) to automatically validate the incoming request body, ensuring it matches the required structure and types, just like ensuring the right gadget fits in its designated pouch. If the data is malformed, FastAPI automatically rejects it (HTTP 422 error), preventing bad data from entering the Batcomputer.

**Memory Aid:**

*   `class MyModel(BaseModel):` = Blueprint for a Gadget/File
*   `field_name: type = Field(...)` = Define required part of the blueprint
*   `field_name: type | None = Field(None, ...)` = Define optional part of the blueprint
*   `@app.post("/path")` = Endpoint for Adding new data
*   `async def func(data: MyModel):` = Expect data matching the blueprint in the request body
*   `/docs` Request Body Section = Shows the blueprint automatically
*   HTTP 422 Error = Data didn't match the blueprint (Wrong gadget!)

---

**Homework:**

1.  **Rogue Profile Model:** Define a new Pydantic model called `RogueProfile` with the following fields:
    *   `alias`: string, required.
    *   `status`: string, optional.
    *   `threat_level`: integer, required, but with a *default value* of `1`. Use `Field(default=1, ge=1, le=10, description="...")` to add validation ensuring the threat level is between 1 and 10 (inclusive). (`ge`=greater than or equal, `le`=less than or equal).
2.  **Create Rogue Endpoint:** Create a `POST /rogues` endpoint that accepts a JSON body matching the `RogueProfile` model. The function should simply print the received profile and return it in a confirmation message.
3.  **Test:** Use `/docs` to test the `/rogues` endpoint. Try sending valid data, data missing optional fields (like `status`), data relying on the default `threat_level`, and invalid data (missing `alias`, `threat_level` outside 1-10). Observe the automatic validation.

**Stretch Goal:**

Add a new field to the `CaseFile` model: `priority: int = Field(default=5, ge=1, le=5)`. This should be an optional integer field (because it has a default) representing priority (1=highest, 5=lowest). Update the `/cases` endpoint (no code changes needed in the function itself!). Test in `/docs` by sending requests with and without the `priority` field, and try sending an invalid priority (e.g., 0 or 6) to see the validation error.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

When you define a Pod in Kubernetes, you specify the container image to run (your packaged application). You can also define **Resource Requests and Limits** (CPU and Memory). Requests guarantee a minimum amount of resources for your Pod (like ensuring the Batcomputer has minimum processing power), while Limits prevent it from consuming excessive resources and impacting other applications on the same node (like preventing a runaway process from hogging all the Batcave's power). Pydantic validates *data*, while Kubernetes resource limits manage *system resources*.
