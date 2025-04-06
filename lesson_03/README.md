# Lesson 3: Detective Mode - Querying Data & External Intel

**Recap:** In Lesson 2, we learned to use the Grappling Hook (Path Parameters) to target specific resources like `/locations/Arkham%20Asylum` or `/gadgets/1`. We saw how type hints provide automatic validation.

Now, we activate **Detective Mode**. This allows Batman to scan environments, filter information, and access external data feeds (like Oracle's network or GCPD reports). Similarly, **Query Parameters** let us filter and customize the data requested from our API, and we'll learn how to fetch data from **External APIs**.

**Core Concepts:**

1.  **Query Parameters:** Optional key-value pairs in the URL (`?key=value&key2=value2`) used for filtering, sorting, or pagination.
2.  **Defining Query Parameters:** Declaring them as default arguments in the endpoint function.
3.  **Optional Parameters & Defaults:** Making queries flexible.
4.  **Combining Path & Query Parameters:** Targeting a resource *and* filtering its data.
5.  **External API Calls:** Using libraries like `httpx` to fetch data from other services.
6.  **Async HTTP Requests:** Making external calls without blocking the server.
7.  **Basic Error Handling:** Dealing with potential issues when calling external APIs.

---

## 1. What are Query Parameters?

While Path Parameters identify *which* resource you want (e.g., `/locations/Arkham%20Asylum`), Query Parameters specify *how* you want it or provide additional filtering criteria. They appear after a `?` in the URL, separated by `&`.

*   `http://127.0.0.1:8000/search-database?keyword=Penguin` (Search for "Penguin")
*   `http://127.0.0.1:8000/search-database?keyword=Joker&limit=5` (Search for "Joker", limit results to 5)
*   `http://127.0.0.1:8000/locations/Iceberg%20Lounge/details?min_threat_level=3` (Get details for Iceberg Lounge, only show threats level 3+)

Here, `keyword`, `limit`, and `min_threat_level` are query parameters.

## 2. Defining Query Parameters in FastAPI

Unlike path parameters (defined in the `@app.get` path string), query parameters are defined simply as **arguments to your endpoint function that are *not* part of the path**. FastAPI is smart enough to figure this out.

**Action:**

*   Create `lesson_03` directory and copy `lesson_02/main.py` into it.
*   Install the `httpx` library for making HTTP requests: `pip install httpx` (ensure your venv is active).
*   Open `lesson_03/main.py` and add the following endpoint:

```python
# main.py (in lesson_03)
# ... (keep imports, app instance, and previous endpoints) ...

# Endpoint with optional query parameters and default values
@app.get("/search-database")
async def search_gotham_database(
    keyword: str | None = None, # Optional: type hint with | None (or Optional[str])
    limit: int = 10 # Optional: provide a default value
    ):
    """
    Searches the Batcomputer database based on an optional keyword and limit.
    """
    # 'keyword' and 'limit' are query parameters because they are function
    # arguments NOT found in the path string "/search-database".

    if keyword:
        return {"searching_for_keyword": keyword, "results_limit": limit}
    else:
        # If 'keyword' isn't provided in the URL (?keyword=...), it will be None
        return {"message": "Provide a 'keyword' query parameter to search the database.", "results_limit": limit}

```

## 3. Optional Parameters & Defaults

*   **Optional:** By type hinting with `| None` (e.g., `keyword: str | None = None`), you tell FastAPI that this query parameter is optional. If the client doesn't include `?keyword=...` in the URL, the value of `keyword` inside your function will be `None`.
*   **Default Value:** By providing a default value (e.g., `limit: int = 10`), the parameter becomes optional. If the client doesn't include `?limit=...`, the value of `limit` inside your function will be `10`.

## 4. Combining Path & Query Parameters

You can easily use both path and query parameters in the same endpoint.

**Action:** Add this endpoint to `lesson_03/main.py`:

```python
# main.py (in lesson_03)

# Endpoint combining path and query parameters
@app.get("/locations/{location_name}/details")
async def get_location_details(
    location_name: str, # Path parameter (defined in path string)
    min_threat_level: int = 0 # Query parameter (not in path string, has default)
    ):
    """
    Gets hypothetical details for a Gotham location, filterable by minimum threat level.
    """
    return {
        "location": location_name.title(),
        "filter_min_threat": min_threat_level,
        "data": f"Intel report for {location_name.title()} with threat level > {min_threat_level} would go here."
        }
```

Here, `location_name` comes from the path, and `min_threat_level` comes from the query string (or defaults to 0).

## 5. Accessing External Intel (Calling External APIs)

Real-world applications often need to interact with other services (external APIs). Batman relies on Oracle, GCPD, etc. We'll use the `httpx` library to make asynchronous HTTP requests to a public placeholder API (JSONPlaceholder) to simulate this.

**Action:** Add the `httpx` import and this endpoint to `lesson_03/main.py`:

```python
# main.py (in lesson_03)
import httpx # Add this import at the top

# ... (other endpoints) ...

# Endpoint fetching data from JSONPlaceholder (External Intel)
@app.get("/fetch-posts")
async def fetch_external_posts(
    limit: int = 5,
    user_id: int | None = None # Stretch Goal parameter
    ):
    """
    Fetches generic posts from JSONPlaceholder API (simulating external intel).
    Demonstrates calling external APIs with httpx.
    """
    external_api_url = "https://jsonplaceholder.typicode.com/posts"
    params = {"_limit": limit} # Parameters for the *external* API
    if user_id is not None:
        params["userId"] = user_id

    # Use httpx.AsyncClient for async requests
    async with httpx.AsyncClient() as client:
        try:
            print(f"Requesting {external_api_url} with params: {params}")
            # Make the GET request asynchronously
            response = await client.get(external_api_url, params=params)
            # Check if the external API returned an error (like 404, 500)
            response.raise_for_status()
            # Parse the JSON response from the external API
            external_data = response.json()

            return {
                "message": f"Successfully fetched {len(external_data)} intel reports (posts) from external source",
                "source": "JSONPlaceholder API (Simulated Intel Feed)",
                "filter_params_sent": params,
                "reports": external_data
            }
        # Handle potential errors during the request
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            return {"error": "Failed to fetch intel from external source", "details": str(exc)}
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            return {
                "error": f"External intel source returned status {exc.response.status_code}",
                "external_url": str(exc.request.url),
                "external_response": exc.response.text
                }

```

Key points:
*   We use `httpx.AsyncClient()` in an `async with` block for proper resource management.
*   `await client.get(...)` makes the request asynchronously, preventing our server from freezing while waiting for the external response.
*   `response.raise_for_status()` checks for HTTP errors (4xx, 5xx) from the external API.
*   `response.json()` parses the JSON data.
*   `try...except` blocks handle potential network errors (`httpx.RequestError`) or bad HTTP responses (`httpx.HTTPStatusError`).

## 6. Testing

**Action:**

1.  Ensure you are in the `lesson_03` directory.
2.  Activate your virtual environment.
3.  Install `httpx`: `pip install httpx`
4.  Run the server: `uvicorn main:app --reload`
5.  Go to `http://127.0.0.1:8000/docs`.
6.  Test the new endpoints:
    *   `/search-database`: Try with and without the `keyword` parameter. Try adding `limit`. (e.g., `?keyword=Two-Face&limit=5`)
    *   `/locations/{location_name}/details`: Try providing a `location_name` in the path and adding `?min_threat_level=...`. (e.g., `/locations/Ace%20Chemicals/details?min_threat_level=8`)
    *   `/fetch-posts`: Try it with default limit, then add `?limit=...`. Try adding `?user_id=...` (Stretch Goal).

---

**Batman Analogy Recap:**

Detective Mode uses Query Parameters (`?keyword=...&limit=...`) to filter data from the Batcomputer (`/search-database`). We can combine targeting (Path Parameters like `/locations/Arkham%20Asylum`) with filtering (Query Parameters like `?min_threat_level=...`). We also learned to pull external intel (`/fetch-posts`) using `httpx` like accessing Oracle's network, handling potential communication errors.

**Memory Aid:**

*   `?key=value&key2=value2` = Query Parameters (Filters for Detective Mode)
*   `func(arg: type | None = None)` = Optional Query Parameter
*   `func(arg: type = default_value)` = Query Parameter with Default
*   `httpx.AsyncClient()` + `await client.get()` = Access External Intel Feeds (Async)
*   `response.raise_for_status()` = Check if Intel Feed Responded Correctly
*   `try...except httpx.RequestError/HTTPStatusError` = Handle Intel Feed Errors

---

**Homework:**

1.  **Filter Gadgets:** Create an endpoint `GET /filter-gadgets`. It should accept two *optional* query parameters: `min_utility` (integer, default 0) and `max_utility` (integer, optional). Return a JSON confirming the filter values being used. Test it via `/docs` with different combinations of parameters.
2.  **Fetch Specific Contact:** Create an endpoint `GET /fetch-contacts/{contact_id}`. It should take an integer `contact_id` as a *path parameter*. Inside the function, use `httpx` to fetch data for that specific user ID from `https://jsonplaceholder.typicode.com/users/{contact_id}`. Return the fetched user data. Implement `try...except` to handle cases where the `contact_id` doesn't exist (JSONPlaceholder will return a 404, which `raise_for_status()` will catch as an `HTTPStatusError`). Test with valid IDs (like 1, 2) and an invalid one (like 999).

**Stretch Goal:**

Modify the `/fetch-posts` endpoint. Add another *optional query parameter* called `user_id` (integer). If `user_id` is provided in the request to *your* API (e.g., `/fetch-posts?limit=3&user_id=1`), pass it along as a query parameter named `userId` to the *external* JSONPlaceholder API request. (Hint: Check the `params` dictionary construction in the example). Test this via `/docs`.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

When your application (Pod/mini Batcave) needs to talk to another service within the same Kubernetes cluster (like another microservice you built), you typically use a Kubernetes "Service." A Service provides a stable internal IP address and DNS name for a set of Pods. This means your Batcave API doesn't need to know the exact, changing IP address of the Oracle microservice Pod; it just talks to the stable "oracle-service" name. Kubernetes handles routing the request to a healthy Pod behind that Service – like a secure, internal comms channel.
