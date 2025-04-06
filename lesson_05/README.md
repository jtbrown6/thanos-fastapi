# Lesson 5: Contingency Plans - Handling Errors Gracefully with HTTPException

**Recap:** In Lesson 4, we learned about the Utility Belt (Pydantic Models) to define blueprints (`CaseFile`, `RogueProfile`) for data received in request bodies (`POST /cases`, `POST /rogues`), ensuring data structure and type validation.

Now, we implement **Contingency Plans**. Batman is always prepared for things to go wrong. What happens if a gadget isn't found in the inventory? What if a user tries to create a contact that already exists? Our API needs to respond with clear, appropriate error messages and HTTP status codes. FastAPI's `HTTPException` is the tool for this.

**Core Concepts:**

1.  **HTTP Status Codes:** Standard codes indicating request outcomes (e.g., `200 OK`, `201 Created`, `404 Not Found`, `400 Bad Request`).
2.  **`HTTPException`:** FastAPI's way to immediately stop processing and return a specific HTTP error response.
3.  **Raising Exceptions:** Using the `raise` keyword with `HTTPException`.
4.  **Common Error Scenarios:** Handling "Not Found" (404) and "Bad Request" (400) errors.
5.  **Custom Error Details:** Providing informative messages in the exception's `detail` field.
6.  **Handling External API Errors:** Propagating or translating errors from services called via `httpx`.

---

## 1. Why Handle Errors Gracefully?

If a user requests `/gadgets/99` and gadget 99 doesn't exist, just crashing or returning a generic `500 Internal Server Error` isn't helpful. The client needs to know *why* the request failed. Returning a `404 Not Found` status code with a clear message like "Gadget not found" is much better.

Similarly, if a user tries to `POST` data to `/contacts` for a contact named "James Gordon" when one already exists, we shouldn't just overwrite it or crash. A `400 Bad Request` with a detail like "Contact already exists" is appropriate.

## 2. Introducing `HTTPException`

FastAPI provides the `HTTPException` class specifically for these situations. When you `raise HTTPException(...)`, FastAPI stops executing the rest of your endpoint function and immediately sends an HTTP response with the status code and detail message you specified.

**Action:**

*   Create `lesson_05` directory and copy `lesson_04/main.py` into it.
*   Open `lesson_05/main.py`.
*   Import `HTTPException` from `fastapi`.
*   Add the simulated databases (`gadget_inventory_db`, `contacts_db`) near the top.
*   Modify the `get_gadget_details` endpoint (previously `locate_stone`) to use `HTTPException`:

```python
# main.py (in lesson_05)
from fastapi import FastAPI, HTTPException # Import HTTPException
# ... other imports, models, app instance ...

# --- Simulate Batcomputer Databases ---
gadget_inventory_db = {
    1: {"name": "Batarang", "type": "Standard Issue", "in_stock": True},
    # ... other gadgets
}
contacts_db = {}
next_contact_id = 1

# ... other endpoints ...

# --- Modified for Lesson 5: GET /gadgets/{gadget_id} ---
@app.get("/gadgets/{gadget_id}")
async def get_gadget_details(gadget_id: int):
    """
    Retrieves details for a specific gadget by its ID from the inventory.
    Returns a 404 error if the gadget ID is not found.
    """
    if gadget_id not in gadget_inventory_db:
        # If the gadget ID is not a key in our simulated DB...
        # ...raise an HTTPException!
        raise HTTPException(
            status_code=404, # Set the HTTP status code (404 Not Found)
            # Provide a helpful detail message for the client
            detail=f"Contingency failed! Gadget with ID {gadget_id} not found in the Batcave inventory."
        )
    # If the 'if' condition is false, execution continues normally
    gadget_data = gadget_inventory_db[gadget_id]
    return {"gadget_id": gadget_id, "status": "Located in inventory", "details": gadget_data}

```

## 3. Handling Bad Requests (400 Errors)

Another common scenario is invalid user input that isn't just a type error (which Pydantic handles) but violates a business rule, like trying to create a duplicate resource.

**Action:** Modify the `create_contact` endpoint (previously `create_character`) to check for duplicates:

```python
# main.py (in lesson_05)

# --- Modified for Lesson 5: POST /contacts ---
@app.post("/contacts", status_code=201) # Set default success status to 201 Created
async def create_contact(contact: Contact):
    """
    Creates a new contact entry. Raises 400 if a contact with the same name already exists.
    """
    global next_contact_id
    # Check for duplicates (case-insensitive) before creating
    for contact_data in contacts_db.values():
        if contact_data["name"].lower() == contact.name.lower():
            # If duplicate found, raise 400 Bad Request
            raise HTTPException(
                status_code=400, # Set status code (400 Bad Request)
                detail=f"Contact named '{contact.name}' already exists in the database."
            )

    # If no exception was raised, proceed to create the contact
    new_id = next_contact_id
    contacts_db[new_id] = contact.model_dump()
    contacts_db[new_id]["id"] = new_id
    next_contact_id += 1

    print(f"Created contact: {contacts_db[new_id]}")
    # Return the newly created contact (FastAPI uses the 201 status code here)
    return contacts_db[new_id]
```
*   We iterate through existing contacts.
*   If a name match is found, we `raise HTTPException` with `status_code=400`.
*   We also set the default success status code for this endpoint to `201 Created` using `status_code=201` in the decorator, which is more appropriate for resource creation.

## 4. Propagating Errors from External APIs

When calling external APIs with `httpx`, errors can occur (network issues, or the external API itself returning 4xx/5xx errors). We should catch these and translate them into appropriate `HTTPException` responses for *our* API's clients.

**Action:** Update the `try...except` blocks in `fetch_external_posts` and `fetch_external_contact` (previously `fetch_external_user`):

```python
# main.py (in lesson_05, inside fetch_external_contact)

    # ... (inside async with httpx.AsyncClient()...)
        try:
            response = await client.get(external_api_url)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx
            contact_data = response.json()
            # ... (return success data) ...
        except httpx.RequestError as exc:
            # Network-level error (DNS, connection refused, etc.)
            # Return 503 Service Unavailable
            raise HTTPException(status_code=503, detail=f"External contact database request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            # Error reported by the external API (4xx or 5xx)
            if exc.response.status_code == 404:
                # Translate external 404 to our 404
                raise HTTPException(status_code=404, detail=f"Contact with ID {contact_id} not found in external source.")
            else:
                # For other external errors, maybe return 502 Bad Gateway
                raise HTTPException(status_code=502,
                                    detail=f"External contact database returned status {exc.response.status_code}: {exc.response.text}")

```
We catch specific `httpx` exceptions and raise corresponding `HTTPException`s with appropriate status codes (503, 404, 502) and informative details.

## 5. Testing Error Handling

**Action:**

1.  Ensure you are in the `lesson_05` directory.
2.  Activate your virtual environment.
3.  Run the server: `uvicorn main:app --reload`
4.  Go to `http://127.0.0.1:8000/docs`.
5.  Test the error scenarios:
    *   `GET /gadgets/99`: Should return a `404 Not Found` with your custom detail message.
    *   `POST /contacts`: First, create a contact successfully (e.g., `{"name": "Lucius Fox", "affiliation": "Wayne Enterprises", "trust_level": 5}`). Should return `201 Created`.
    *   `POST /contacts` again with the *same name* (`{"name": "Lucius Fox", "affiliation": "CEO"}`). Should return a `400 Bad Request` with the duplicate error detail.
    *   `GET /fetch-contacts/999`: Should return a `404 Not Found` (originating from the `HTTPStatusError` catch block).
    *   (Harder to test 503/502 without disrupting network/JSONPlaceholder).

---

**Batman Analogy Recap:**

Contingency Plans (`HTTPException`) are crucial when things go wrong. If a requested gadget isn't found (`GET /gadgets/99`), we raise a `404 Not Found` exception. If the user tries to add a duplicate contact (`POST /contacts`), we raise a `400 Bad Request`. When external intel feeds (like JSONPlaceholder) fail or return errors, we catch those (`httpx` exceptions) and raise appropriate `HTTPException`s (like `404`, `503 Service Unavailable`, `502 Bad Gateway`) to inform the client clearly about the failure, maintaining control even in unexpected situations.

**Memory Aid:**

*   `from fastapi import HTTPException` = Import the Contingency Plan tool
*   `raise HTTPException(status_code=XXX, detail="...")` = Execute Contingency Plan XXX
*   `status_code=404` = Plan for "Not Found"
*   `status_code=400` = Plan for "Bad Request" (e.g., duplicate data)
*   `status_code=503` = Plan for "External Service Unavailable" (Network Error)
*   `status_code=502` = Plan for "Bad Gateway" (External Service Error)
*   `try...except httpx.Error: raise HTTPException(...)` = Translate external failures into internal plans

---

**Homework:**

1.  **Duplicate Gadget Check:** Modify the `POST /gadgets` endpoint (created in Lesson 4 homework, now updated in `lesson_05/main.py`). Add logic similar to `POST /contacts` to check if a gadget with the same `name` (case-insensitive) already exists in the `gadget_inventory_db`. If it does, `raise HTTPException` with `status_code=400` and an appropriate detail message.
2.  **Test:** Use `/docs` to test your modified `POST /gadgets`. Try creating a new gadget spec, then try creating one with the same name (e.g., "Batarang") and verify you get the 400 error.

**Stretch Goal:**

Modify the `GET /fetch-contacts/{contact_id}` endpoint. Currently, it raises a 502 error for any non-404 HTTP error from the external API. Change it so that if the external API returns a `400 Bad Request` (status code 400), *your* API also returns a `400 Bad Request` `HTTPException`, perhaps with a detail indicating an issue with the requested ID format according to the external source. For any *other* external HTTP errors (e.g., 500, 503), continue raising a `502 Bad Gateway`. Test this (though simulating an external 400 might be tricky without finding an API that reliably returns one for specific inputs).

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

Kubernetes uses **Readiness and Liveness Probes** as contingency plans for Pods.
*   **Liveness Probe:** Checks if the application inside the container is still running (alive). If it fails repeatedly, Kubernetes restarts the container (like rebooting the Batcomputer if it freezes).
*   **Readiness Probe:** Checks if the application is ready to serve traffic. If it fails, Kubernetes stops sending new requests to that Pod until the probe succeeds again (like taking a Batmobile offline for repairs without stopping the whole operation).
FastAPI's `HTTPException` handles *request-level* errors, while Kubernetes probes handle *application/Pod health* errors.
