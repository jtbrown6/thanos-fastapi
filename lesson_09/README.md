# Lesson 9: Batcave Security Protocols - Middleware & CORS

**Recap:** In Lesson 8, we built the Batcave Display, learning to serve static files (`StaticFiles`) like CSS and render dynamic HTML (`Jinja2Templates`, `TemplateResponse`) to create a user-facing web interface.

Now, we implement **Batcave Security Protocols**. Every request entering or leaving the Batcomputer network needs to pass through checks. **Middleware** allows us to intercept and process *every* incoming request before it hits a specific endpoint and *every* outgoing response before it's sent back. We'll use this for logging, adding headers, and crucially, configuring **Cross-Origin Resource Sharing (CORS)** to control which web pages (origins) are allowed to access our API.

**Core Concepts:**

1.  **Middleware:** Code that runs for every request/response, sitting between the server and your endpoint logic.
2.  **Use Cases:** Logging, adding custom headers, authentication checks, CORS, compression, etc.
3.  **`@app.middleware("http")`:** Decorator for defining custom asynchronous HTTP middleware.
4.  **Middleware Function Signature:** `async def func(request: Request, call_next)`
5.  **Processing Requests:** Code before `await call_next(request)`.
6.  **Processing Responses:** Code after `await call_next(request)`.
7.  **CORS (Cross-Origin Resource Sharing):** Browser security mechanism preventing web pages from making requests to a different domain (origin) than the one that served the page, unless explicitly allowed by the server.
8.  **`CORSMiddleware`:** FastAPI's built-in middleware for configuring CORS headers.
9.  **`allow_origins`:** Specifying which frontend domains are permitted to access the API.

---

## 1. What is Middleware?

Think of middleware as security checkpoints or processing stations that every request and response must pass through.

*   **Request Path:** Client -> Middleware 1 -> Middleware 2 -> Endpoint Logic
*   **Response Path:** Endpoint Logic -> Middleware 2 -> Middleware 1 -> Client

This allows us to apply common logic globally without adding it to every single endpoint function.

## 2. Custom Middleware: Adding Process Time

Let's create a simple middleware to measure how long each request takes to process and add that information as a custom header to the response.

**Action:**

*   Create `lesson_09` directory and copy `lesson_08/main.py` into it.
*   Open `lesson_09/main.py`.
*   Import `time`.
*   Define and add the middleware using the `@app.middleware("http")` decorator:

```python
# main.py (in lesson_09)
import time
from fastapi import FastAPI, Request
# ... other imports ...

app = FastAPI(...) # Keep title/description/version from previous step

# --- Custom Middleware Definitions ---

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """ Adds X-Process-Time header to responses. """
    start_time = time.time()
    # Process the request by calling the next middleware or the endpoint
    response = await call_next(request)
    # Code here runs AFTER the response has been generated
    process_time = time.time() - start_time
    # Add a custom header to the response
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(f"Request to {request.url.path} processed in {process_time:.4f} sec")
    return response

# ... rest of the app setup (mount static, templates, etc.) ...
# ... endpoints ...
```
*   The function takes `request: Request` and `call_next`.
*   `call_next` is a function that receives the `request` and passes it along the chain (to the next middleware or the endpoint). You **must** `await call_next(request)` and return its `response`.
*   Code *before* `await call_next` processes the incoming request.
*   Code *after* `await call_next` processes the outgoing response.

## 3. CORS: Allowing Web Pages to Access Your API

By default, browsers block JavaScript running on `http://my-cool-site.com` from making `fetch` requests to your API running on `http://127.0.0.1:8000` (a different origin). This is the **Same-Origin Policy**.

To allow `my-cool-site.com` to access your API, your API server needs to include specific **CORS headers** (like `Access-Control-Allow-Origin`) in its responses. FastAPI's `CORSMiddleware` handles this.

**Action:**

*   In `lesson_09/main.py`, import `CORSMiddleware`.
*   Define the list of allowed `origins`.
*   Add the `CORSMiddleware` to the app **before** defining routes or other middleware if possible.

```python
# main.py (in lesson_09)
from fastapi.middleware.cors import CORSMiddleware # Import

app = FastAPI(...)

# --- CORS Middleware Definition ---
# IMPORTANT: Add CORS middleware EARLY, ideally before routes/other middleware.
origins = [
    "http://localhost",       # Allow standard localhost (often needed for dev)
    "http://localhost:8080",  # Allow common frontend dev server port
    "http://127.0.0.1",       # Allow loopback IP
    "http://127.0.0.1:8080",  # Allow loopback IP with port
    "null",                   # Allow requests from local files (origin 'null')
    # In production, list your actual frontend domain(s):
    # "https://batman-frontend.wayne.enterprises",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Which origins can access the API
    allow_credentials=True,    # Allow cookies/auth headers to be sent
    allow_methods=["*"],       # Allow all standard HTTP methods (GET, POST, etc.)
    allow_headers=["*"],       # Allow all headers
)

# --- Custom Middleware Definitions ---
# (add_process_time_header, add_api_version_header)

# --- Mount Static Files & Configure Templates ---
# ...

# --- Endpoints ---
# ...
```
*   `allow_origins`: A list of strings specifying allowed frontend origins. Use `"*"` to allow *any* origin (use with caution!).
*   `allow_credentials`: Set to `True` if your frontend needs to send cookies or `Authorization` headers.
*   `allow_methods`: Which HTTP methods are allowed (e.g., `["GET", "POST"]`). `"*"` allows all.
*   `allow_headers`: Which request headers are allowed. `"*"` allows all.

## 4. Testing Middleware

**Action:**

1.  Run the server: `uvicorn main:app --reload`
2.  Use `/docs` or tools like `curl` or Postman to make requests to any endpoint (e.g., `GET /`).
3.  **Check Response Headers:** Look for the `X-Process-Time` and `X-API-Version` (Homework) headers added by your custom middleware.
4.  **Check CORS Headers:** Look for headers like `Access-Control-Allow-Origin` in the response. Its value should match one of your allowed origins (or `*` if you used that).
5.  **Test CORS (Optional but Recommended):**
    *   Create a simple local HTML file (e.g., `test_cors.html`) on your computer.
    *   Add JavaScript to `fetch` data from your API (e.g., `fetch('http://127.0.0.1:8000/')`).
    *   Open the HTML file directly in your browser (its origin will be `null`).
    *   Open the browser's developer console (usually F12).
    *   If CORS is configured correctly (including `"null"` in `origins`), the `fetch` should succeed. If not, you'll see a CORS error in the console.

---

**Batman Analogy Recap:**

Batcave Security Protocols (Middleware) act as checkpoints. The `add_process_time_header` middleware is like a system monitor logging entry/exit times for every request. `CORSMiddleware` is the main gatekeeper, checking the origin (where the request comes from) against an approved list (`origins`) before allowing access, preventing unauthorized domains (like Arkham Asylum's network) from directly querying the Batcomputer API via a browser.

**Memory Aid:**

*   `@app.middleware("http")` = Define a Security Checkpoint (Custom Middleware)
*   `async def checkpoint(request, call_next): response = await call_next(request); return response` = Middleware Structure
*   Code *before* `await call_next` = Check incoming request.
*   Code *after* `await call_next` = Modify outgoing response (e.g., add headers).
*   `from fastapi.middleware.cors import CORSMiddleware` = Import the Gatekeeper Protocol (CORS)
*   `app.add_middleware(CORSMiddleware, allow_origins=[...], ...)` = Configure the Gatekeeper
*   `allow_origins`: List of approved domains/locations allowed to access via browser JS.

---

**Homework:**

1.  **API Version Middleware:** Create another custom middleware function `add_api_version_header(request, call_next)`. This middleware should add a custom header `X-API-Version` to every response. The value of the header should be the `app.version` string defined when creating the `FastAPI` instance.
2.  **Add Middleware:** Add this new middleware to your app using `@app.middleware("http")`.
3.  **Test:** Run the app and use `/docs` or `curl` to check if the `X-API-Version` header appears in the responses along with `X-Process-Time`.

**Stretch Goal:**

Configure the `CORSMiddleware` with more restrictive settings. Instead of allowing all methods (`allow_methods=["*"]`) and all headers (`allow_headers=["*"]`), try limiting it:
*   `allow_methods=["GET", "POST"]`
*   `allow_headers=["Content-Type", "X-API-Key"]` (Allowing a common request header and our custom auth header from Lesson 6).
Test if you can still access `GET` endpoints and `POST` endpoints (like `/contacts`) from `/docs`. Try accessing an endpoint that requires the `X-API-Key` header (like `/gcpd-files` if you kept it) - does it still work? What happens if a frontend tries to send a different custom header? (It should be blocked by the browser due to CORS preflight checks failing).

*(Find the complete code for this lesson in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

In Kubernetes, **Network Policies** act like firewalls between Pods and Namespaces. They control which Pods can communicate with each other based on labels, IP addresses, or ports. While `CORSMiddleware` controls access at the application layer based on the browser's `Origin` header, Kubernetes Network Policies control access at the network layer based on Pod identities and network rules, providing a deeper layer of security within the cluster. You might use both: Network Policies to restrict which services *can* talk to your API Pod, and CORS to restrict which *web origins* can talk to your API via a browser.
