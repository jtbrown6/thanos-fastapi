# Lesson 5: Vormir's Sacrifice - Handling Errors Gracefully with `HTTPException`

**Recap:** In Lesson 4, we used the Eye of Agamotto (Pydantic Models) to structure and validate incoming data from the request body, especially for `POST` requests. We saw how FastAPI automatically handles validation errors (422).

Our journey now takes us to the desolate planet Vormir, location of the Soul Stone. Acquiring it demands a terrible sacrifice – a testament to the fact that sometimes, things go wrong, and we must handle the consequences. In API development, automatic validation catches many errors, but often our *own application logic* encounters situations where a request cannot be fulfilled. We need a way to explicitly signal these errors back to the client. This is where FastAPI's `HTTPException` comes in.

**Core Concepts:**

1.  **Beyond Automatic Validation:** Errors arising from application logic (e.g., resource not found).
2.  **`HTTPException`:** FastAPI's standard way to return HTTP error responses.
3.  **Status Codes:** Communicating the type of error (e.g., 404 Not Found, 400 Bad Request).
4.  **Detail Messages:** Providing specific error information to the client.
5.  **Raising Exceptions:** How to trigger an error response from your code.

---

## 1. When Automatic Validation Isn't Enough

Pydantic and FastAPI automatically handle errors related to incorrect data types or missing required fields in path parameters, query parameters, and request bodies (usually resulting in a `422 Unprocessable Entity` response).

But what about errors specific to your application's logic?

*   What if a user requests `/stones/99`, and stone ID 99 simply doesn't exist in your database? This isn't a *validation* error (99 is a valid integer), but a *logical* error – the requested resource is not found.
*   What if a user tries to perform an action they don't have permission for?
*   What if a required external service is temporarily unavailable?

In these cases, simply returning a default `200 OK` response would be misleading or incorrect. We need to explicitly tell the client, "Sorry, I couldn't fulfill your request because [reason]."

## 2. Introducing `HTTPException`

FastAPI provides the `HTTPException` class as the standard way to signal these kinds of errors. When you `raise` an `HTTPException` from within your endpoint function, FastAPI catches it and sends the appropriate HTTP error response to the client.

**Key Arguments for `HTTPException`:**

*   `status_code`: An integer representing the standard HTTP status code for the error (e.g., `404`, `400`, `403`).
*   `detail`: A message (string or JSON-encodable object) providing specific details about the error. This message will be included in the response body sent to the client.
*   `headers`: Optional dictionary of custom headers to include in the error response.

## 3. Common HTTP Status Codes for Errors

You should use standard HTTP status codes to communicate the nature of the error:

*   **`400 Bad Request`:** General client-side error (e.g., invalid input that wasn't caught by validation, illogical request).
*   **`401 Unauthorized`:** Client needs to authenticate (provide credentials).
*   **`403 Forbidden`:** Client is authenticated, but doesn't have permission to access the resource.
*   **`404 Not Found`:** The requested resource does not exist. **(Very common!)**
*   **`422 Unprocessable Entity`:** (Often handled automatically by FastAPI/Pydantic) The request was well-formed, but contained semantic errors (e.g., invalid data values according to validation rules).
*   **`500 Internal Server Error`:** A generic error occurred on the server side that wasn't expected. You usually want to avoid returning this directly unless something truly unexpected happened.

## 4. Raising `HTTPException` in Your Code

Let's modify our `GET /stones/{stone_id}` endpoint. Currently, it just returns the ID regardless of whether it's valid. Let's simulate having a small collection of known stones and return a `404 Not Found` error if the requested ID isn't in our collection.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_05`
*   Copy `main.py` from `lesson_04` into `lesson_05`: `cp lesson_04/main.py lesson_05/`
*   Open `fastapi-gauntlet-course/lesson_05/main.py`.
*   Import `HTTPException` from `fastapi`.
*   Add a simple dictionary to simulate stored data.
*   Modify the `locate_stone` endpoint:

```python
# main.py (in lesson_05)
from fastapi import FastAPI, HTTPException # Import HTTPException
import httpx
from pydantic import BaseModel

# ... (keep app instance and Pydantic models) ...

# Simulate a database or collection of known stones
# In a real app, this would come from a database query
known_stones_db = {
    1: {"name": "Space", "location": "Tesseract", "color": "Blue"},
    2: {"name": "Mind", "location": "Scepter/Vision", "color": "Yellow"},
    3: {"name": "Reality", "location": "Aether", "color": "Red"},
    4: {"name": "Power", "location": "Orb/Gauntlet", "color": "Purple"},
    5: {"name": "Time", "location": "Eye of Agamotto", "color": "Green"},
    6: {"name": "Soul", "location": "Vormir/Gauntlet", "color": "Orange"}
}

# ... (keep other endpoints like read_root, scan_planet, etc.) ...

# --- Modify the /stones/{stone_id} endpoint ---
@app.get("/stones/{stone_id}")
async def locate_stone(stone_id: int): # Still expects an integer path parameter
    """
    Retrieves details for a specific stone by its ID.
    Returns a 404 error if the stone ID is not found.
    """
    # Check if the requested stone_id exists in our 'database'
    if stone_id not in known_stones_db:
        # If not found, raise HTTPException
        # This immediately stops function execution and sends the error response.
        raise HTTPException(
            status_code=404, # Set the HTTP status code
            detail=f"Sacrifice failed! Stone with ID {stone_id} not found on Vormir (or anywhere else)."
        )
    
    # If the stone_id *is* found, return its data
    stone_data = known_stones_db[stone_id]
    return {"stone_id": stone_id, "status": "Located", "details": stone_data}

# ... (keep other endpoints like create_stone, create_character, etc.) ...

```

**Explanation:**

1.  We import `HTTPException`.
2.  We create `known_stones_db` (a dictionary) to act as our simple data store.
3.  Inside `locate_stone`, *before* trying to access the data, we check `if stone_id not in known_stones_db:`.
4.  If the ID is *not* found, we `raise HTTPException(...)`. We provide:
    *   `status_code=404` (Not Found).
    *   `detail` (a helpful message for the client).
5.  If the `if` condition is false (meaning the ID *was* found), the `raise` statement is skipped, and the function continues normally, retrieving and returning the stone's data with a `200 OK` status.

## 5. Testing Error Handling

Let's see how this behaves.

**Action:**

1.  Make sure you are in the `lesson_05` directory.
2.  Activate your virtual environment.
3.  Run the server: `uvicorn main:app --reload`
4.  Go to `http://127.0.0.1:8000/docs`.
5.  Find the `GET /stones/{stone_id}` endpoint. Expand it.
6.  Click "**Try it out**".
7.  **Test Success:** Enter a valid ID (e.g., `1`, `5`). Execute. You should get a `200 OK` response with the stone details.
8.  **Test Failure (404):** Enter an invalid ID (e.g., `99`, `0`, `-1`). Execute. Observe the response:
    *   The **Status Code** should be `404 Not Found`.
    *   The **Response Body** should contain the `detail` message you specified in the `HTTPException`.
9.  Try accessing directly in the browser:
    *   `http://127.0.0.1:8000/stones/6` (Success)
    *   `http://127.0.0.1:8000/stones/10` (Failure - 404)

You've successfully implemented custom error handling!

---

**Thanos Analogy Recap:**

Obtaining the Soul Stone on Vormir required a specific condition (a sacrifice). If the condition wasn't met, the quest failed. Our `GET /stones/{stone_id}` endpoint now has a condition (`if stone_id not in known_stones_db`). If the condition fails, we make the necessary *sacrifice* (`raise HTTPException`) to signal the failure (`404 Not Found`) clearly, rather than pretending everything is fine.

**Memory Aid:**

*   `if condition_fails:` = Check Vormir's Requirement
*   `raise HTTPException(status_code=404, detail="...")` = Make the Sacrifice (Signal Not Found)
*   `404` = Resource Not Found (Soul Stone not obtainable for you!)
*   `detail` = Red Skull's explanation of why you failed.

---

**Homework:**

1.  Modify the `POST /stones` endpoint (where we create stones). Add a check *before* printing/returning: if the `name` of the stone being created already exists in the `known_stones_db` (you'll need to iterate through the dictionary values to check names), raise an `HTTPException` with `status_code=400` (Bad Request) and a detail message like "Stone with this name already exists."
2.  Test this new validation using `/docs`. Try creating a stone with a unique name, then try creating one with a name that's already in `known_stones_db` (e.g., "Time"). Observe the `400` error.

**Stretch Goal:**

Modify the `GET /fetch-users/{user_id}` endpoint from Lesson 3. Instead of just returning the error dictionary when `httpx.HTTPStatusError` occurs (especially for a 404 from JSONPlaceholder), catch that specific exception and `raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found in external source.")`. This makes your API's error response more consistent with the `/stones/{stone_id}` endpoint.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

How does Kubernetes know if your application Pod is actually healthy and ready to serve requests, or if it has crashed or gotten stuck? It uses "Liveness Probes" and "Readiness Probes."
*   **Liveness Probe:** Checks if the container is still running correctly. If it fails repeatedly, Kubernetes will "sacrifice" the Pod (kill it and restart it).
*   **Readiness Probe:** Checks if the container is ready to accept traffic. If it fails, Kubernetes temporarily removes the Pod from the associated Service endpoints, preventing traffic from being sent to an unhealthy instance.
These probes are crucial for maintaining application health and ensuring graceful handling of Pod failures in a cluster – the automated Vormir trials for your application instances.
