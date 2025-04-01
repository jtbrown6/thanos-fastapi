# Lesson 4: The Eye of Agamotto - Structuring Time (and Data) with Pydantic

**Recap:** In Lesson 3, we used the Aether (Query Parameters) to reshape requests and `httpx` to interact with external API realities. We learned the importance of reading API documentation.

Now, we seek the Eye of Agamotto, the Time Stone. It allows its user to perceive and structure time. In API development, we often need to receive complex, structured data from the client – data that doesn't fit neatly into simple path or query parameters. **Pydantic Models** are FastAPI's way of defining and enforcing the *structure* of this data across the *time* of a request-response cycle.

**Core Concepts:**

1.  **Request Body:** Sending complex data to the API.
2.  **HTTP Methods (POST, PUT, PATCH):** Operations that typically use request bodies.
3.  **Pydantic `BaseModel`:** Defining data structures/schemas.
4.  **Benefits of Pydantic:** Validation, serialization, documentation, editor support.
5.  **Using Models in Endpoints:** Automatic request body handling.
6.  **Accessing Model Data:** Using dot notation.
7.  **Testing with `/docs`:** Sending JSON request bodies.

---

## 1. When URLs Aren't Enough: The Request Body

So far, we've only sent data *to* the server via the URL itself (path and query parameters). This is great for simple values or identifying resources. But what if a client needs to send a *new*, complex object to be created? For example, creating a new Infinity Stone entry in our system, including its name, description, power level, and location? Putting all that in a URL would be messy and impractical.

This is where the **Request Body** comes in. It allows the client to send a larger chunk of data (commonly formatted as JSON) along with the HTTP request, separate from the URL.

## 2. HTTP Methods for Sending Data

While `GET` is primarily for retrieving data, other HTTP methods are designed for operations that often involve sending data in the request body:

*   **`POST`:** Typically used to **create** a new resource. (e.g., add a new stone to the collection).
*   **`PUT`:** Typically used to **replace** an existing resource entirely. (e.g., update all details of stone ID 5).
*   **`PATCH`:** Typically used to **partially update** an existing resource. (e.g., just change the location of stone ID 3).

FastAPI supports decorators for all these: `@app.post()`, `@app.put()`, `@app.patch()`, etc.

## 3. Structuring Data: Enter Pydantic `BaseModel`

Okay, so the client sends JSON data in the request body. How does our FastAPI application know what structure to expect? How does it validate that the client sent the correct fields with the correct data types?

Manually parsing and validating JSON dictionaries would be tedious and error-prone. This is where **Pydantic** shines. Pydantic is a data validation and settings management library that FastAPI leverages heavily.

We define the expected structure using a Python class that inherits from Pydantic's `BaseModel`.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_04`
*   Copy `main.py` from `lesson_03` into `lesson_04`: `cp lesson_03/main.py lesson_04/`
*   Open `fastapi-gauntlet-course/lesson_04/main.py`.
*   Import `BaseModel` and define a simple `Stone` model:

```python
# main.py (in lesson_04)
from fastapi import FastAPI
import httpx
from pydantic import BaseModel # Import BaseModel

app = FastAPI()

# --- Define Pydantic Models ---

class Stone(BaseModel):
    # Define fields with type hints
    name: str # This field is required because it has no default value
    description: str | None = None # Optional field (can be string or None)
    # We'll add more fields later

# ... (keep previous endpoints from lessons 1-3) ...
```

This `Stone` class defines a data structure:
*   It *must* have a `name` field, and its value must be a string.
*   It *may* have a `description` field, which, if present, must be a string. If not provided, it defaults to `None`.

## 4. Why Pydantic is Your Eye of Agamotto

Using Pydantic models gives you superpowers:

*   **Data Validation:** If a client sends JSON that doesn't match the model (e.g., `name` is missing or is a number, `description` is an integer), Pydantic automatically raises a validation error, and FastAPI returns a helpful `422 Unprocessable Entity` response detailing the exact problem – *before* your endpoint code runs. It ensures data conforms to the expected structure, preventing errors down the line.
*   **Data Serialization:** Pydantic handles converting the incoming JSON into a Python object (`Stone` instance) for you to use easily. It can also serialize your Pydantic objects back into JSON for responses.
*   **Automatic Documentation:** FastAPI uses your Pydantic models to generate a detailed JSON Schema in the `/docs` interface, showing clients exactly what data structure is expected in the request body.
*   **Editor Support:** Because models are just Python classes, you get excellent autocompletion and type checking in your editor when working with model instances.

## 5. Using Models in Endpoints

How do you tell FastAPI to expect a `Stone` object in the request body for a specific endpoint? Just like with path and query parameters: use a type hint in the function signature!

**Action:** Add a `POST` endpoint to create stones:

```python
# main.py (in lesson_04, add new endpoint)

# ... (keep app instance, Stone model, and previous endpoints) ...

@app.post("/stones")
# Type hint 'stone: Stone' tells FastAPI to:
# 1. Expect JSON in the request body.
# 2. Validate the JSON against the 'Stone' model.
# 3. If valid, convert it into a 'Stone' object and pass it as the 'stone' argument.
async def create_stone(stone: Stone):
    """
    Creates a new stone entry.
    Expects a JSON body conforming to the Stone model.
    """
    print(f"Received stone data: Name={stone.name}, Description={stone.description}")
    
    # In a real app, you would save this 'stone' object to a database here.
    
    # Return a confirmation message, potentially including the received data
    # Pydantic v1: stone.dict()
    # Pydantic v2+: stone.model_dump()
    return {"message": f"Stone '{stone.name}' created successfully.", "received_data": stone.model_dump()}

```

That's it! FastAPI, powered by Pydantic, handles all the parsing and validation of the request body based on the `stone: Stone` type hint.

## 6. Accessing Model Data

Inside your `create_stone` function, the `stone` argument is a regular Python object (an instance of your `Stone` class). You access its fields using standard dot notation:

*   `stone.name`
*   `stone.description`

## 7. Testing POST Requests with `/docs`

How do you send a JSON request body to test this? The `/docs` interface makes it easy!

**Action:**

1.  Make sure you are in the `lesson_04` directory.
2.  Activate your virtual environment.
3.  Run the server: `uvicorn main:app --reload`
4.  Go to `http://127.0.0.1:8000/docs`.
5.  Find the new `POST /stones` endpoint. Expand it.
6.  Notice the "Request body" section. It shows an *example* JSON based on your `Stone` model and the detailed *schema*.
7.  Click "**Try it out**".
8.  The example request body becomes editable. Modify it if you like.
    *   **Valid Example:**
        ```json
        {
          "name": "Soul",
          "description": "Requires a great sacrifice."
        }
        ```
    *   **Another Valid Example (optional field omitted):**
        ```json
        {
          "name": "Mind"
        }
        ```
9.  Click "**Execute**". You should get a `200 OK` response with your confirmation message. Check the terminal where Uvicorn is running – you should see the `print` statement output.
10. **Test Validation:** Now, try sending *invalid* data. Edit the request body:
    *   **Invalid (missing required 'name'):**
        ```json
        {
          "description": "Floats mysteriously."
        }
        ```
    *   **Invalid (wrong type for 'name'):**
        ```json
        {
          "name": 123,
          "description": "A number?"
        }
        ```
11. Execute these invalid requests. Observe the response: you should get a `422 Unprocessable Entity` status code, and the response body will detail exactly *which* field failed validation and why. This is Pydantic and FastAPI working together!

---

**Thanos Analogy Recap:**

The Eye of Agamotto structures time. Pydantic `BaseModel` structures the *data* sent in requests, ensuring consistency and validity *over time* (across different client requests). It validates incoming data structures, preventing temporal paradoxes (malformed data!) before they reach your core logic. `/docs` lets you experiment with sending different data structures through the time stream.

**Memory Aid:**

*   `class MyModel(BaseModel):` = Define Data Structure Blueprint
*   `field: type` = Rule for that part of the structure
*   `endpoint(data: MyModel)` = Expect & Validate Structure in Request Body
*   `data.field` = Access structured data
*   `422 Error` = Structure Violation Detected!

---

**Homework:**

1.  Define a new Pydantic model called `Character` with the following fields:
    *   `name: str` (required)
    *   `affiliation: str | None = None` (optional string, e.g., "Avengers", "Guardians", "Black Order")
    *   `power_level: int = 0` (required integer, defaulting to 0)
2.  Create a `POST /characters` endpoint that accepts a `Character` object in the request body.
3.  The endpoint should simply return the received character data using `.model_dump()`.
4.  Test creating various characters using `/docs`, including valid ones and ones that trigger validation errors (missing name, wrong type for power_level).

**Stretch Goal:**

Add a new *required* field `acquired: bool` to the `Stone` model defined earlier in the lesson. Does your existing `POST /stones` endpoint still work if the client *doesn't* send the `acquired` field in the JSON? (It shouldn't - required fields must be provided). Update your tests in `/docs` to include the `acquired` field (e.g., `"acquired": true`).

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

When deploying applications that need persistent storage (like a database to store the 'stones' or 'characters' we create via POST requests), simple container storage isn't enough because it disappears when the Pod restarts. Kubernetes uses "PersistentVolumes" (PVs) - representing underlying storage like a network disk - and "PersistentVolumeClaims" (PVCs) - requests for storage made by your application. You mount the PVC as a "Volume" inside your Pod, giving your application durable storage that survives restarts, much like the Soul Stone persists even after Vormir's trials.
