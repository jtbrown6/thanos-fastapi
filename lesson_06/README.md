# Lesson 6: Batcomputer Protocols - Dependency Injection

**Recap:** In Lesson 5, we implemented Contingency Plans (`HTTPException`) to handle errors gracefully, returning appropriate status codes like `404 Not Found` or `400 Bad Request` when things go wrong (e.g., gadget not found, duplicate contact).

Now, we establish **Batcomputer Protocols**. Complex systems like the Batcomputer rely on shared logic and resources (authentication, database connections, common parameters). Instead of repeating this code in every endpoint, we can define reusable components called **Dependencies** and have FastAPI automatically "inject" them where needed. This is **Dependency Injection (DI)**.

**Core Concepts:**

1.  **Code Reusability:** Avoiding repetition of common logic (e.g., pagination parameters, user authentication).
2.  **Separation of Concerns:** Keeping endpoint logic focused on its specific task, delegating common tasks to dependencies.
3.  **`Depends`:** The FastAPI function used to declare a dependency in an endpoint's signature.
4.  **Dependencies as Functions:** Defining dependencies as simple `async def` or `def` functions.
5.  **Dependencies with `yield`:** Creating dependencies that manage resources (like database connections) with setup and teardown logic.
6.  **Dependencies on Dependencies:** Building complex logic by having dependencies that rely on other dependencies (e.g., verifying a user *after* getting their authentication token).
7.  **Sharing Dependencies:** Using the same dependency across multiple endpoints.
8.  **Type Hinting Dependencies:** Using `typing.Annotated` for cleaner dependency declaration.

---

## 1. The Problem: Repetitive Code

Imagine multiple endpoints need pagination (`skip`, `limit` query parameters) or need to verify an API key from a header. Copying and pasting that logic into every endpoint is inefficient and error-prone.

## 2. The Solution: Dependency Injection with `Depends`

FastAPI's DI system lets you define this logic *once* in a separate function (a dependency) and then declare that your endpoint *depends* on it. FastAPI runs the dependency function for each request to that endpoint and provides ("injects") the result into your endpoint function.

**Action:**

*   Create `lesson_06` directory and copy `lesson_05/main.py` into it.
*   Open `lesson_06/main.py`.
*   Import `Depends`, `Header` from `fastapi` and `Annotated` from `typing`.

## 3. Simple Dependency: Common Query Parameters

Let's create a dependency to handle common pagination parameters.

**Action:** Define the `common_parameters` function and the `CommonsDep` type alias:

```python
# main.py (in lesson_06)
from fastapi import Depends # Import Depends
from typing import Annotated

# ... other imports, models, app instance ...

# --- Dependencies for Lesson 6 ---

# Simple dependency providing common query parameters
async def common_parameters(skip: int = 0, limit: int = 100):
    """ Provides common query parameters for pagination. """
    # This function looks like an endpoint function, taking query parameters.
    print(f"Dependency 'common_parameters' called with skip={skip}, limit={limit}")
    # The dictionary it returns will be injected into endpoints that depend on it.
    return {"skip": skip, "limit": limit}

# Type alias using Annotated for cleaner endpoint signatures
# This says: CommonsDep is a dict, and its value comes from Depends(common_parameters)
CommonsDep = Annotated[dict, Depends(common_parameters)]

# ... (rest of the code)
```

Now, use this dependency in an endpoint:

**Action:** Add the `/items/` endpoint:

```python
# main.py (in lesson_06)

# ... (dependencies defined above) ...

# --- New Endpoints for Lesson 6 ---

@app.get("/items/")
async def read_items(commons: CommonsDep): # Use the dependency via the type alias
    """ Reads generic items using common pagination parameters from DI. """
    # FastAPI sees 'Depends(common_parameters)' in CommonsDep.
    # It calls common_parameters(skip=..., limit=...) using query params from the request.
    # The returned dictionary {"skip": ..., "limit": ...} is passed as the 'commons' argument.
    print(f"Endpoint '/items/' using common pagination: {commons}")

    all_item_ids = [f"item_{i}" for i in range(1, 501)]
    start = commons['skip']
    end = start + commons['limit']
    paginated_items = all_item_ids[start:end]
    return {"skip": commons['skip'], "limit": commons['limit'], "items": paginated_items}

# You can reuse the SAME dependency in another endpoint:
@app.get("/list-contacts/")
async def list_contacts(commons: CommonsDep): # Reuse CommonsDep
    """ Lists contacts using common pagination parameters from DI. """
    print(f"Endpoint '/list-contacts/' using common pagination: {commons}")
    # ... (logic to fetch and paginate contacts using commons['skip'] and commons['limit']) ...
    all_contact_ids = list(contacts_db.keys()) # Assuming contacts_db exists
    start = commons['skip']
    end = start + commons['limit']
    paginated_contact_ids = all_contact_ids[start:end]
    paginated_contacts = [contacts_db.get(cid, {}) for cid in paginated_contact_ids]
    return {"skip": commons['skip'], "limit": commons['limit'], "contacts": paginated_contacts}

```
FastAPI automatically handles calling `common_parameters` and passing its result to `read_items` and `list_contacts`.

## 4. Dependencies with `yield`: Resource Management

Dependencies are perfect for managing resources that need setup and teardown, like database connections. A dependency function using `yield` can perform setup before the `yield` and teardown after.

**Action:** Define the `get_db_session` dependency:

```python
# main.py (in lesson_06)

# Dependency with yield for resource management (e.g., DB session)
async def get_db_session():
    """ Simulates acquiring and releasing a database session using yield. """
    print("==> Simulating DB connection open <==")
    db_session = {"id": hash(str(id({}))), "status": "connected", "data": {}} # Simulate unique session
    try:
        # Code before yield runs before the endpoint.
        # The yielded value is injected into the endpoint.
        yield db_session
    finally:
        # Code after yield runs *after* the endpoint finishes,
        # even if the endpoint raised an exception. Perfect for cleanup!
        print(f"==> Simulating DB connection close (Session ID: {db_session['id']}) <==")

DBSessionDep = Annotated[dict, Depends(get_db_session)]
```

**Action:** Add endpoints using this dependency:

```python
# main.py (in lesson_06)

@app.get("/batcomputer-logs")
async def get_logs(db: DBSessionDep): # Use the yielding dependency
    """ Reads logs using a dependency-managed DB session (simulation). """
    print(f"--- Endpoint using Batcomputer DB session ID: {db.get('id')} ---")
    db["data"]["log_entry_1"] = "Accessed gadget inventory." # Use the injected session
    return {"message": "Log data accessed using DB session", "session_details": db}

@app.get("/batcomputer-logs-error")
async def get_logs_error(db: DBSessionDep):
    """ Simulates an error occurring while using the DB session for logs. """
    print(f"--- Endpoint (error case) using Batcomputer DB session ID: {db.get('id')} ---")
    db["data"]["log_entry_error"] = "Attempting risky operation..."
    raise HTTPException(status_code=500, detail="Batcomputer core meltdown simulated!")
    # Even though we raise an error here, the 'finally' block in get_db_session will execute.
```
When you call these endpoints, check the terminal output to see the "open" and "close" messages, demonstrating the setup/teardown lifecycle managed by the dependency.

## 5. Dependencies Calling Other Dependencies: Chaining Protocols

Dependencies can depend on other dependencies. This allows building layers of logic (e.g., first get an API key, then verify it).

**Action:** Define `get_api_key` and `verify_key_and_get_user` dependencies:

```python
# main.py (in lesson_06)
from fastapi import Header

# Dependency to get API Key from header
async def get_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    """ Dependency to extract an API key from the X-API-Key header. """
    print(f"API Key dependency checking header: {x_api_key}")
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing (Authentication required)")
    return x_api_key

APIKeyDep = Annotated[str, Depends(get_api_key)]

# Dependency that depends on another dependency (verify API key)
async def verify_key_and_get_user(api_key: APIKeyDep): # Depends on get_api_key via APIKeyDep
    """ Dependency that depends on get_api_key and verifies it (simulated). """
    # FastAPI sees api_key: APIKeyDep. It knows APIKeyDep means Depends(get_api_key).
    # So, it first calls get_api_key() and passes the result here as 'api_key'.
    print(f"Verifying API key: {api_key}")
    if api_key != "gcpd-secret-key-789": # Simulate checking the key
        raise HTTPException(status_code=403, detail="Invalid API Key provided (Access Denied)")

    user_data = {"user_id": "gcpd_officer_jim", "permissions": ["read_cases"]}
    print(f"API Key verified, returning user data: {user_data}")
    return user_data # This user_data is injected into the endpoint

VerifiedUserDep = Annotated[dict, Depends(verify_key_and_get_user)]
```

**Action:** Add an endpoint using the chained dependency:

```python
# main.py (in lesson_06)

@app.get("/gcpd-files")
async def read_gcpd_files(current_user: VerifiedUserDep): # Depends on verify_key_and_get_user
     """ Accesses secure GCPD files, requiring a valid API key via dependencies. """
     # FastAPI calls verify_key_and_get_user, which calls get_api_key.
     # The final result (user_data) from verify_key_and_get_user is injected here.
     print(f"Endpoint accessing GCPD files for user: {current_user.get('user_id')}")
     return {"message": "Access granted to secure GCPD files.", "accessed_by": current_user}
```

## 6. Testing Dependencies

**Action:**

1.  Run the server: `uvicorn main:app --reload`
2.  Go to `http://127.0.0.1:8000/docs`.
3.  Test the new endpoints:
    *   `/items/`: Try adding `?skip=...` and `?limit=...`. Observe terminal output for `common_parameters`.
    *   `/list-contacts/`: Try adding `?limit=...`. Observe reuse of `common_parameters`.
    *   `/batcomputer-logs`: Call it. Observe "open" and "close" messages in terminal.
    *   `/batcomputer-logs-error`: Call it. Observe the 500 error, but *also* the "open" and "close" messages in terminal (finally block runs).
    *   `/gcpd-files`: Click "Try it out". Add a Header parameter named `X-API-Key` with value `gcpd-secret-key-789`. Execute. Should succeed.
    *   `/gcpd-files`: Try again with a *wrong* `X-API-Key` value. Should get 403 Forbidden.
    *   `/gcpd-files`: Try again *without* the `X-API-Key` header. Should get 401 Unauthorized.

---

**Batman Analogy Recap:**

Batcomputer Protocols (Dependencies) allow us to define reusable logic. `common_parameters` is like a standard pagination protocol used by multiple endpoints (`/items/`, `/list-contacts/`). `get_db_session` is a protocol for safely connecting and disconnecting from the Batcomputer's core database, ensuring cleanup even if errors occur (`yield`). `get_api_key` and `verify_key_and_get_user` form a chained security protocol: first check for credentials (`X-API-Key`), then verify them before granting access (`/gcpd-files`). `Depends` is the mechanism that links endpoints to these protocols.

**Memory Aid:**

*   `async def my_dependency(...): return value` = Define a Reusable Protocol
*   `DepType = Annotated[ReturnType, Depends(my_dependency)]` = Create Alias for Protocol
*   `async def my_endpoint(result: DepType):` = Use the Protocol (Inject Result)
*   `async def resource_mgr(): try: yield resource finally: cleanup` = Protocol with Setup/Teardown
*   `async def protocol_b(result_a: DepTypeA):` = Protocol B depends on Protocol A

---

**Homework:**

1.  **Current User Dependency:** Create an `async def get_current_user():` dependency that simulates fetching user data (e.g., return a dictionary like `{"username": "batman", "email": "...", "is_active": True}`).
2.  **`/contacts/me` Endpoint:** Create a `GET /contacts/me` endpoint that depends on `get_current_user` and simply returns the user data provided by the dependency.
3.  **Inactive User Check:** Modify the `get_current_user` dependency: if the simulated user's `"is_active"` field is `False`, raise an `HTTPException` with `status_code=400` and detail "User account is inactive." Test `/contacts/me` in both active and inactive states (by temporarily changing the simulated data in the dependency).

**Stretch Goal:**

1.  **Admin Verification Dependency:** Create a new dependency `async def verify_admin_user(current_user: CurrentUserDep):` which *depends on* your `get_current_user` dependency (use the `CurrentUserDep` alias). Inside `verify_admin_user`, check if `current_user['username']` is equal to `"batman"`. If not, raise an `HTTPException` with `status_code=403` (Forbidden) and detail "Admin privileges required." If it *is* "batman", simply return the `current_user` dictionary.
2.  **Admin Panel Endpoint:** Create a `GET /batcave/control-panel` endpoint that depends on your new `verify_admin_user` dependency. It should return a simple success message if access is granted.
3.  **Test:** Test `/batcave/control-panel` (it should work if `get_current_user` returns "batman"). Then, temporarily modify `get_current_user` to return a different username (e.g., "robin") and test `/batcave/control-panel` again – it should now fail with a 403 error.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

Dependencies in FastAPI share some conceptual similarity with **Sidecar Containers** in Kubernetes. A sidecar is an additional container running in the same Pod as your main application container. It shares the same network and storage, and often handles cross-cutting concerns like logging, monitoring, service discovery, or acting as a proxy – tasks that support the main application without being part of its core logic. Just like FastAPI dependencies handle tasks like authentication or DB connections alongside your endpoint logic, sidecars handle infrastructure tasks alongside your application container.
