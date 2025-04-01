# Lesson 6: The Mind Stone's Influence - Dependency Injection

**Recap:** On Vormir in Lesson 5, we learned the necessity of sacrifice (`HTTPException`) to handle errors gracefully when application logic fails (like a 404 Not Found).

Now, we consider the Mind Stone. It grants its wielder great intelligence, control, and the ability to influence others. In FastAPI, the **Dependency Injection (DI)** system acts similarly: it allows us to define reusable components ("dependencies") that provide data, connections, or perform actions (like shared knowledge or tools) and then *inject* them into our endpoint functions as needed. This promotes cleaner, more reusable, and more testable code.

**Core Concepts:**

1.  **What is Dependency Injection?** Sharing logic and resources.
2.  **Why Use DI?** Code reuse, separation of concerns, easier testing.
3.  **Creating Dependencies:** Simple functions that provide a value or resource.
4.  **Using `Depends`:** Declaring dependencies in endpoint function signatures.
5.  **Dependency Execution:** How FastAPI runs dependencies.
6.  **Dependencies with `yield`:** Managing resources like database connections.
7.  **Dependencies Calling Other Dependencies:** Building complex dependency chains.

---

## 1. What is Dependency Injection?

Imagine several of your endpoints need access to the same information (like the current user's permissions) or need to perform the same setup task (like getting a database connection). Instead of repeating that logic in every single endpoint function, you can define it *once* in a separate function – a **dependency**.

Then, you tell FastAPI that your endpoint function *depends* on this other function. FastAPI will automatically run the dependency function first and pass its result (the "injected" value) into your endpoint function as an argument.

It's like the Mind Stone granting specific knowledge (the dependency's result) to an individual (the endpoint function) exactly when they need it.

## 2. Why Use Dependency Injection? The Benefits

*   **Code Reuse:** Write common logic once (e.g., getting the current user, validating an API key, connecting to a database) and reuse it across multiple endpoints just by declaring the dependency.
*   **Separation of Concerns:** Endpoint functions can focus on their core task, delegating tasks like authentication or data access to dependencies. This makes code cleaner and easier to understand.
*   **Easier Testing:** You can easily provide "mock" or fake dependencies during testing, allowing you to test endpoint logic in isolation without needing a real database or external service. (We'll cover testing more later).
*   **Editor Support:** You get full type hinting and autocompletion for the values provided by dependencies.
*   **Automatic Documentation:** Dependencies can be integrated into FastAPI's automatic documentation.

## 3. Creating a Simple Dependency

A dependency is often just a regular Python function (it can be `def` or `async def`). Its purpose is to return a value or yield a resource that the endpoint needs.

**Example:** Let's create a dependency that provides some common query parameters for pagination.

```python
# main.py (in lesson_06)

# --- Dependency Function ---
async def common_parameters(skip: int = 0, limit: int = 100):
    """
    Provides common query parameters for pagination.
    This function itself receives query parameters from the request.
    """
    # This dependency simply returns the validated parameters as a dictionary.
    return {"skip": skip, "limit": limit}
```

This function `common_parameters` takes optional `skip` and `limit` query parameters (just like an endpoint function could!) and returns them in a dictionary.

## 4. Using `Depends` to Inject Dependencies

How do we tell an endpoint function that it needs the result of `common_parameters`? We use `Depends` from `fastapi`.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_06`
*   Copy `main.py` from `lesson_05` into `lesson_06`: `cp lesson_05/main.py lesson_06/`
*   Open `fastapi-gauntlet-course/lesson_06/main.py`.
*   Import `Depends` from `fastapi`.
*   Add the `common_parameters` dependency function shown above.
*   Add a new endpoint that uses this dependency:

```python
# main.py (in lesson_06)
from fastapi import FastAPI, HTTPException, Depends # Import Depends
import httpx
from pydantic import BaseModel

# ... (keep app instance, models, known_stones_db, characters_db) ...

# --- Dependency Function ---
async def common_parameters(skip: int = 0, limit: int = 100):
    """ Provides common query parameters for pagination. """
    return {"skip": skip, "limit": limit}

# ... (keep previous endpoints) ...

# --- New Endpoint Using Dependency Injection ---
@app.get("/items/")
# 'commons: dict = Depends(common_parameters)' tells FastAPI:
# 1. Before running 'read_items', run 'common_parameters'.
# 2. 'common_parameters' might need query parameters 'skip' and 'limit' from the request.
# 3. Take the dictionary returned by 'common_parameters' and pass it as the 'commons' argument.
async def read_items(commons: dict = Depends(common_parameters)):
    """
    Reads a list of hypothetical items, using common pagination parameters
    provided by the 'common_parameters' dependency.
    """
    print(f"Received common parameters via DI: {commons}")
    
    # In a real app, you'd use commons['skip'] and commons['limit']
    # in your database query.
    # Example: items = db.query(Item).offset(commons['skip']).limit(commons['limit']).all()
    
    # Simulate returning items based on pagination
    all_item_ids = list(range(1000)) # Simulate 1000 items
    start = commons['skip']
    end = start + commons['limit']
    paginated_items = all_item_ids[start:end]
    
    return {"skip": commons['skip'], "limit": commons['limit'], "items": paginated_items}

# Let's add another endpoint using the same dependency!
@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    """
    Reads a list of hypothetical users, also using the common pagination dependency.
    Demonstrates reusability.
    """
    print(f"Received common parameters via DI: {commons}")
    # Simulate returning users
    all_user_ids = ["User_A", "User_B", "User_C", "User_D", "User_E"] # Simulate fewer users
    start = commons['skip']
    end = start + commons['limit']
    paginated_users = all_user_ids[start:end]
    
    return {"skip": commons['skip'], "limit": commons['limit'], "users": paginated_users}

# ... (keep other endpoints) ...
```

**Explanation:**

1.  We import `Depends`.
2.  We define `common_parameters` which takes `skip` and `limit` (these will be populated from the request's query parameters, just as if they were defined directly on the endpoint).
3.  In `read_items` and `read_users`, the argument `commons: dict = Depends(common_parameters)` declares the dependency.
    *   `Depends(common_parameters)` tells FastAPI to call `common_parameters`.
    *   `commons: dict` receives the *result* returned by `common_parameters`.
4.  Now, both `/items/` and `/users/` accept `skip` and `limit` query parameters, but the logic for handling them is centralized in `common_parameters`.

**Action:** Run `uvicorn main:app --reload` and test:

*   `/docs`: See how `/items/` and `/users/` now both list `skip` and `limit` as query parameters, inherited from the dependency.
*   `/items/` (uses defaults `skip=0`, `limit=100`)
*   `/items/?skip=10&limit=5`
*   `/users/` (uses defaults)
*   `/users/?skip=1&limit=2`

## 5. Dependency Execution Flow

When a request comes in for `/items/?skip=10&limit=5`:

1.  FastAPI sees that `read_items` depends on `common_parameters`.
2.  FastAPI checks if `common_parameters` needs any parameters itself (yes: `skip` and `limit`).
3.  FastAPI extracts `skip=10` and `limit=5` from the request's query string.
4.  FastAPI calls `common_parameters(skip=10, limit=5)`.
5.  `common_parameters` returns `{"skip": 10, "limit": 5}`.
6.  FastAPI calls `read_items(commons={"skip": 10, "limit": 5})`.
7.  `read_items` executes its logic using the `commons` dictionary.

## 6. Dependencies with `yield`: Managing Resources

What if a dependency needs to set something up (like opening a database connection) and then clean it up afterwards (close the connection), regardless of whether the endpoint succeeded or failed? Dependencies can use `yield`.

```python
# main.py (in lesson_06, add this dependency example)

# --- Dependency with yield (Resource Management) ---
async def get_db_session():
    """
    Simulates acquiring and releasing a database session.
    Uses 'yield' to manage the resource lifecycle.
    """
    print("==> Simulating DB connection open <==")
    # Code before yield runs before the endpoint
    db_session = {"id": 123, "status": "connected", "data": {}} 
    try:
        yield db_session # The yielded value is injected into the endpoint
    finally:
        # Code after yield runs *after* the endpoint finishes (even if errors occurred)
        print("==> Simulating DB connection close <==")
        # In a real DB session: session.close()

# --- Endpoint using the yielding dependency ---
@app.get("/data-from-db")
async def get_data(db: dict = Depends(get_db_session)):
    """ Reads hypothetical data using a dependency-managed DB session. """
    print(f"--- Endpoint using DB session ID: {db.get('id')} ---")
    # Simulate using the session
    db["data"]["item1"] = "value1" 
    return {"message": "Data accessed using DB session", "session_details": db}

# --- Endpoint that causes an error while using the session ---
@app.get("/data-from-db-error")
async def get_data_error(db: dict = Depends(get_db_session)):
    """ Simulates an error occurring while using the DB session. """
    print(f"--- Endpoint (error case) using DB session ID: {db.get('id')} ---")
    # Simulate using the session then causing an error
    db["data"]["item1"] = "value1"
    raise HTTPException(status_code=500, detail="Something went wrong in the endpoint!")
    # Notice the 'finally' block in get_db_session will still run!

```

**Explanation:**

1.  `get_db_session` simulates opening a connection before the `yield`.
2.  It `yield`s the session object (`db_session`). This value is injected into the endpoint.
3.  The endpoint (`get_data` or `get_data_error`) runs.
4.  *After* the endpoint finishes (or raises an exception), the code in the `finally` block of `get_db_session` runs, ensuring cleanup (simulated connection close).

**Action:** Test `/data-from-db` and `/data-from-db-error` via `/docs`. Observe the print statements in your terminal to see the "open" and "close" messages wrapping the endpoint execution, even when an error occurs.

## 7. Dependencies Calling Other Dependencies

Dependencies can depend on other dependencies! FastAPI handles resolving the chain.

```python
# main.py (in lesson_06, add these examples)

# --- More Dependencies ---
async def get_api_key(api_key: str | None = Depends(lambda: Header(None, alias="X-API-Key"))):
     """ Dependency to extract an API key from the X-API-Key header. """
     # Using Header directly inside Depends requires a lambda or separate function
     # We'll cover Headers more later, this is just for DI demo.
     print(f"API Key dependency checking header: {api_key}")
     if not api_key:
         raise HTTPException(status_code=401, detail="X-API-Key header missing")
     return api_key

async def verify_key_and_get_user(api_key: str = Depends(get_api_key)):
     """ Dependency that depends on get_api_key and verifies it. """
     print(f"Verifying API key: {api_key}")
     if api_key != "fake-secret-key-123": # Simulate checking the key
         raise HTTPException(status_code=403, detail="Invalid API Key provided")
     # Simulate fetching user based on key
     return {"user_id": "user_for_" + api_key, "permissions": ["read"]}

# --- Endpoint using the dependent dependency ---
@app.get("/secure-data")
# This endpoint only needs to depend on the *final* dependency in the chain.
# FastAPI figures out that verify_key_and_get_user needs get_api_key.
async def read_secure_data(current_user: dict = Depends(verify_key_and_get_user)):
     """ Accesses secure data, requiring a valid API key via dependencies. """
     print(f"Endpoint accessing data for user: {current_user.get('user_id')}")
     return {"message": "This is secure data.", "accessed_by": current_user}

```
*(Note: We need `Header` for the `get_api_key` example)*
**Action:** Add `Header` to the `fastapi` import: `from fastapi import FastAPI, HTTPException, Depends, Header`. Test `/secure-data` via `/docs`. You'll need to use the "Try it out" feature to add the `X-API-Key` header. Try with no header, the wrong key, and the correct key (`fake-secret-key-123`).

---

**Thanos Analogy Recap:**

The Mind Stone grants knowledge and influence. Dependency Injection (`Depends`) *influences* your endpoints by providing necessary *knowledge* (data like pagination params) or *tools* (like a DB session or user info) obtained from reusable dependency functions. Dependencies can even influence each other, creating chains of knowledge acquisition, all managed seamlessly by FastAPI.

**Memory Aid:**

*   `Depends(dependency_func)` = Inject Knowledge/Tool
*   `dependency_func()` = The Source of Knowledge/Tool
*   `yield` in dependency = Manage Tool Lifecycle (Setup/Cleanup)
*   DI Chain = Mind Stone influencing an intermediary who then influences the final target.

---

**Homework:**

1.  Create a simple dependency function `get_current_user()` that simulates fetching user data and returns a dictionary like `{"username": "thanos", "email": "thanos@titan.net", "is_active": True}`.
2.  Create an endpoint `GET /users/me` that uses `Depends(get_current_user)` to get the user data and returns it.
3.  Modify the `get_current_user` dependency: add a check so that if `is_active` is `False` in the returned dictionary, it raises an `HTTPException` with `status_code=400` and detail "Inactive user". Test this by temporarily changing the simulated user data.

**Stretch Goal:**

Create a dependency `verify_admin_user` that itself depends on `get_current_user`. Inside `verify_admin_user`, check if the `username` from the user data is "thanos". If it's not "thanos", raise an `HTTPException` with `status_code=403` (Forbidden) and detail "Admin privileges required". Create an endpoint `GET /admin/panel` that depends on `verify_admin_user` and returns `{"message": "Welcome, Admin!"}`. Test it (it should only work if `get_current_user` returns the "thanos" username).

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

How do applications running in Kubernetes get configuration like database URLs, API keys for external services, or logging levels? Hardcoding is bad. Kubernetes offers "ConfigMaps" for non-sensitive configuration and "Secrets" for sensitive data (like API keys, passwords). These can be *injected* into your Pods as environment variables or mounted as files. This is conceptually similar to Dependency Injection – the Kubernetes cluster *injects* necessary configuration *dependencies* into your application's environment at runtime, decoupling the application code from its configuration.
