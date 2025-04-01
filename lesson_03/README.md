# Lesson 3: The Aether - Shaping Reality with Query Parameters & External APIs

**Recap:** In Lesson 2, we harnessed the Orb's power with Path Parameters (`/planets/{planet_name}`) to target specific resources. We saw how FastAPI uses type hints for automatic validation.

Now, we encounter the Aether, the Reality Stone. It allows its wielder to reshape reality itself. **Query Parameters** give the *client* calling our API the power to reshape or filter the request, asking for specific variations or subsets of data. We'll also use this opportunity to reach out beyond our own API and interact with the vast reality of external APIs!

**Core Concepts:**

1.  **Query Parameters vs. Path Parameters:** Understanding the difference.
2.  **Defining Query Parameters:** Declaring them as function arguments.
3.  **Optional Parameters & Default Values:** Making queries flexible.
4.  **Combining Path and Query Parameters:** Using both in one endpoint.
5.  **Calling External APIs:** Using `httpx` to fetch data.
6.  **Reading Basic API Documentation:** Understanding how to use external services.

---

## 1. Path vs. Query Parameters: Know Your Reality

It's crucial to understand when to use each:

*   **Path Parameters (Lesson 2):** Identify a *specific resource*. They are part of the core path structure.
    *   Example: `/stones/1` (identifies the stone with ID 1)
    *   Example: `/planets/Xandar` (identifies the planet Xandar)
*   **Query Parameters (This Lesson):** *Filter, sort, or modify* the request for a resource or collection. They appear *after* a `?` in the URL and are key-value pairs separated by `&`.
    *   Example: `/search?term=Gauntlet` (searches for "Gauntlet")
    *   Example: `/items?skip=0&limit=10` (gets items, skipping 0, limiting to 10)
    *   Example: `/planets?min_population=1000000&sort=name` (filters planets by population and sorts them)

Think of it like this: Path parameters define *which* reality (resource) you're looking at, while query parameters let you *alter* or *specify details* about that reality.

## 2. Defining Query Parameters

You define query parameters simply by adding them as arguments to your endpoint function, **as long as they are *not* already defined as path parameters in the decorator.**

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_03`
*   Copy `main.py` from `lesson_02` into `lesson_03`: `cp lesson_02/main.py lesson_03/`
*   Open `fastapi-gauntlet-course/lesson_03/main.py`.
*   Add the following endpoint:

```python
# main.py (in lesson_03)
# ... (keep imports, app instance, and previous endpoints) ...

# New endpoint demonstrating a query parameter
@app.get("/search")
# 'term' is NOT in the path "/search", so FastAPI treats it as a query parameter.
async def search_reality(term: str): # Required query parameter 'term'
    return {"searching_for": term}
```

If you run this and go to `/docs`, you'll see `term` listed under "Parameters" as a *query* parameter, marked as required. If you try to access `/search` in your browser without providing the query parameter (e.g., `http://127.0.0.1:8000/search`), FastAPI will give you an error because `term` is required! You need to provide it like this: `http://127.0.0.1:8000/search?term=Infinity`.

## 3. Optional Parameters and Default Values

Often, query parameters are optional filters. How do we define them?

*   **Using `| None = None`:** (Recommended in modern Python) This makes the parameter optional. If the client doesn't provide it, the variable will be `None` inside your function.
*   **Using `Optional[type] = None`:** (Older Python versions) Does the same thing. You'd need `from typing import Optional`.
*   **Providing a Default Value:** `limit: int = 10`. If the client doesn't provide `limit`, it will default to `10` inside your function. This also makes the parameter optional.

**Action:** Modify the `/search` endpoint to make `term` optional and add an optional `limit`:

```python
# main.py (in lesson_03, update /search endpoint)
# You might need: from typing import Optional (if using older Python)

@app.get("/search")
async def search_reality(
    term: str | None = None, # Make 'term' optional
    limit: int = 10 # Add 'limit' with a default value (also optional)
    ):
    if term:
        return {"searching_for": term, "results_limit": limit}
    else:
        # Handle the case where 'term' was not provided
        return {"message": "Provide a 'term' query parameter to search.", "results_limit": limit}
```

Now, `/search` works without parameters (using defaults), `/search?term=Stones` works, `/search?limit=5` works, and `/search?term=Thanos&limit=1` works! Test these variations in `/docs` and your browser.

## 4. Combining Path and Query Parameters

You can absolutely use both in the same endpoint!

Example: Get details about a specific planet, but allow filtering by power level.

```python
# main.py (in lesson_03, add new endpoint)

@app.get("/planets/{planet_name}/info") # Path parameter: planet_name
async def get_planet_info(
    planet_name: str, # Path parameter received here
    min_power: int = 0 # Query parameter received here
    ):
    # In a real app, you might query a database using both parameters
    return {
        "planet": planet_name.capitalize(),
        "filter_min_power": min_power,
        "data": f"Details about {planet_name.capitalize()} with power > {min_power} would go here."
        }
```

Test this via `/docs` or browser: `http://127.0.0.1:8000/planets/Xandar/info?min_power=500`.

## 5. Reaching Beyond: Calling External APIs with `httpx`

Our API doesn't have to exist in a vacuum! It can interact with other APIs on the web to fetch data, perform actions, etc. A popular library for making HTTP requests in modern Python (especially with `async`) is `httpx`.

**Action:** Install `httpx`:

*   Make sure your virtual environment is active.
*   Run: `pip install httpx`

Now, let's use it to fetch data from a public API. We'll use **JSONPlaceholder** ([https://jsonplaceholder.typicode.com/](https://jsonplaceholder.typicode.com/)), a great free service for testing and prototyping that provides fake API data (posts, comments, users, etc.).

## 6. Reading Basic API Documentation

Before using *any* external API, you MUST look at its documentation. It tells you:

*   **Available Endpoints:** What URLs can you call? (e.g., `/posts`, `/users/{id}`)
*   **HTTP Methods:** What method should you use for each endpoint? (GET, POST, etc.)
*   **Required/Optional Parameters:** Does it expect path parameters? Query parameters? Request bodies?
*   **Authentication:** Does it require an API key or other credentials? (JSONPlaceholder doesn't, which is why it's great for starting).
*   **Response Format:** What does the data look like when it comes back? (Usually JSON).

**JSONPlaceholder Example (`/posts` endpoint):**

Looking at their site (or just knowing common patterns), we can infer:

*   **Endpoint:** `https://jsonplaceholder.typicode.com/posts`
*   **Method:** `GET` (to retrieve posts)
*   **Parameters (Query):** They support filtering/pagination like `_limit` (e.g., `?_limit=5` to get only 5 posts) and `userId` (e.g., `?userId=1` to get posts by user 1).
*   **Authentication:** None needed.
*   **Response:** An array of JSON objects, each representing a post with keys like `userId`, `id`, `title`, `body`.

**Action:** Let's create an endpoint in *our* API that fetches posts from JSONPlaceholder.

```python
# main.py (in lesson_03, add imports and new endpoint)
import httpx # Import the httpx library

# ... (FastAPI app instance and other endpoints) ...

# Endpoint to fetch data from an external API
@app.get("/fetch-posts")
async def fetch_external_posts(limit: int = 5): # Our API takes an optional limit
    """
    Fetches posts from the JSONPlaceholder API.
    Allows specifying a limit via query parameter.
    """
    # The URL of the external API endpoint
    external_api_url = "https://jsonplaceholder.typicode.com/posts"
    
    # Parameters to send to the external API
    params = {"_limit": limit} # JSONPlaceholder uses _limit

    # Use an async context manager for httpx client
    async with httpx.AsyncClient() as client:
        try:
            # Make the asynchronous GET request
            response = await client.get(external_api_url, params=params)
            
            # Raise an exception if the request failed (e.g., 4xx or 5xx errors)
            response.raise_for_status() 
            
            # Parse the JSON response from the external API
            external_data = response.json()
            
            return {
                "message": f"Successfully fetched {len(external_data)} posts from JSONPlaceholder",
                "source": "JSONPlaceholder API",
                "posts": external_data
            }
        except httpx.RequestError as exc:
            # Handle potential errors during the request (e.g., network issues)
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            # You might want to return a proper HTTP error from your API here
            return {"error": "Failed to fetch data from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            # Handle errors reported by the external API (like 404 Not Found, 500 Server Error)
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
            return {"error": f"External API returned status {exc.response.status_code}", "details": exc.response.text}

```

**Explanation:**

1.  We import `httpx`.
2.  We define our endpoint `/fetch-posts` which accepts an optional `limit` query parameter.
3.  We define the `external_api_url`.
4.  We create a `params` dictionary for the query parameters *JSONPlaceholder* expects (`_limit`).
5.  We use `async with httpx.AsyncClient() as client:` which creates an asynchronous HTTP client session (efficient for multiple requests, though we only make one here).
6.  `response = await client.get(external_api_url, params=params)`: This is the core line. We `await` the result of the `GET` request made by `httpx` to the external URL, passing our desired query parameters.
7.  `response.raise_for_status()`: Checks if the external API returned an error status code (like 404 or 500). If so, it raises an exception.
8.  `external_data = response.json()`: Parses the JSON data received from JSONPlaceholder.
9.  We return this fetched data wrapped in our own API's response structure.
10. We include `try...except` blocks to gracefully handle potential network errors (`httpx.RequestError`) or error responses from the external API (`httpx.HTTPStatusError`).

**Action:** Run `uvicorn main:app --reload` and test `/fetch-posts` and `/fetch-posts?limit=3` in `/docs`. You should see post data fetched live from JSONPlaceholder!

---

**Thanos Analogy Recap:**

The Aether reshapes reality. Query parameters (`?limit=10`) let clients *reshape* the requests they send to our API. We then used `httpx` to peer into *another reality* (the JSONPlaceholder API), read its *rules* (documentation), and pull data from it, incorporating it into our own response. Error handling ensures we don't break our reality if the external one is unavailable.

**Memory Aid:**

*   `?key=value` = Reshape Request (Query Param)
*   `param: type | None = None` = Optional Reality
*   `param: type = default` = Default Reality
*   `httpx.get(url)` = Peer into External Reality
*   API Docs = Rules of the External Reality

---

**Homework:**

1.  Create an endpoint `GET /filter_stones` (similar to Lesson 2's stretch goal) that accepts two optional query parameters: `min_power: int = 0` and `max_power: int | None = None`. Return both values in the response. Test various combinations using `/docs`.
2.  Look at the JSONPlaceholder documentation for the `/users` endpoint (`https://jsonplaceholder.typicode.com/users`). Create a new endpoint in your API `GET /fetch-users/{user_id}` that:
    *   Takes a `user_id` as a **path parameter**.
    *   Uses `httpx` to call `https://jsonplaceholder.typicode.com/users/{user_id}` (substituting the correct ID).
    *   Returns the user data fetched from JSONPlaceholder.
    *   Include error handling similar to the `/fetch-posts` example.
    *   Test it with `/docs` for valid IDs (e.g., 1, 2) and an invalid ID (e.g., 999 - observe the error returned from JSONPlaceholder via your API).

**Stretch Goal:**

Modify the `/fetch-posts` endpoint. Add another optional query parameter to *your* API called `user_id: int | None = None`. If `user_id` is provided to your API, pass it as the `userId` query parameter to the JSONPlaceholder API request (`params = {"_limit": limit, "userId": user_id}`). This allows filtering posts by user *through* your API. Test `/fetch-posts?user_id=1&limit=2`.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

When your application needs external configuration (like the URL for an external API, API keys, or database connection strings), you don't want to hardcode them in your container image. Kubernetes provides "ConfigMaps" for general configuration and "Secrets" for sensitive data. These can be injected into your Pods as environment variables or files, allowing you to configure your application without rebuilding the container image – keeping your reality flexible.
