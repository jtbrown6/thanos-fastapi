# Lesson 1: The Bat-Signal - Creating Your First API Endpoint

**Welcome, Rookie!** Batman uses the Bat-Signal to be alerted to trouble in Gotham. Our first step is similar: we need to create the fundamental *signal* for our API to exist and respond. We'll set up our project, write the simplest possible API, and run it.

**Core Concepts:**

1.  **Environment Setup:** Keeping projects organized in the Batcave.
2.  **FastAPI & Uvicorn:** The core library and the server (like the Batcomputer and its power source).
3.  **The `FastAPI` Instance:** The heart of our application.
4.  **Route Decorators (`@app.get`)**: Connecting URLs (signals) to code (responses).
5.  **Endpoint Functions (`async def`)**: Where the crime-fighting logic happens.
6.  **Returning Data (JSON):** Sending information back (case files).
7.  **Running the Server:** Powering up the Batcomputer.
8.  **Using `/docs`:** Your interactive crime map/database.

---

## 1. Setting Up Your Batcave (Environment Setup)

Before building advanced gadgets, a well-organized Batcave is essential. In Python, we use **virtual environments** to keep the tools (packages) for different projects separate. This prevents conflicts – you wouldn't want tools for the Batmobile mixing with those for Alfred's tea kettle!

**Action:**

*   Open your terminal or command prompt.
*   Navigate to where you want to create your project folder (e.g., `Documents/Projects`).
*   Create the main course directory: `mkdir fastapi-batman-course`
*   Navigate into it: `cd fastapi-batman-course`
*   Create the directory for this lesson: `mkdir lesson_01`
*   Navigate into it: `cd lesson_01`
*   Create a virtual environment: `python -m venv venv` (or `python3 -m venv venv`)
    *   This creates a `venv` folder containing a copy of Python and tools.
*   Activate the environment:
    *   **macOS/Linux:** `source venv/bin/activate`
    *   **Windows:** `venv\Scripts\activate`
    *   You should see `(venv)` appear at the start of your terminal prompt.

## 2. Gathering the Gadgets (Installing FastAPI & Uvicorn)

Now, let's gather the core gadgets:

*   **FastAPI:** The framework itself – provides the structure and tools to build APIs quickly (like the Utility Belt's core components).
*   **Uvicorn:** An ASGI server. Think of FastAPI as the blueprint for a gadget, and Uvicorn as the power source that makes it work. ASGI (Asynchronous Server Gateway Interface) is a standard that allows Python web frameworks to handle many requests efficiently.

**Action:**

*   With your virtual environment active, run:
    `pip install "fastapi[all]"`
    *   `pip` is Python's package installer.
    *   `"fastapi[all]"` installs FastAPI and recommended dependencies, including Uvicorn and Pydantic (which we'll use later).

## 3. Forging the Core: The `FastAPI` Instance

Every mission needs a starting point. In FastAPI, this is an instance of the `FastAPI` class.

**Action:**

*   Create a file named `main.py` inside your `lesson_01` directory (if you haven't already from the previous step).
*   Add the following code:

```python
# main.py - Step 1: Import the necessary class
from fastapi import FastAPI

# Step 2: Create an instance of the FastAPI class
# This 'app' object is the main point of interaction for creating your API.
app = FastAPI()
```

This `app` object is like the central console in the Batcave from which our API operations will be coordinated. We'll use it to define paths, handle requests, and more.

## 4. Lighting the Signal: Route Decorators (`@app.get`)

Commissioner Gordon uses the Bat-Signal to call Batman. We use **route decorators** to connect URL paths (the signal's location) to our Python functions (Batman's response). A decorator is a special syntax in Python (starting with `@`) that modifies or enhances a function.

`@app.get("/")` tells FastAPI: "When someone sends an HTTP GET request to the root path (`/`) of the server (like shining the signal at the default location), execute the function defined immediately below this line."

*   **HTTP GET:** This is one of the standard methods used on the web, typically used for *retrieving* data. When you type a URL in your browser, it usually sends a GET request.

## 5. The Response Protocol: Endpoint Functions (`async def`)

Where does the signal lead? To an **endpoint function**. This is the Python code that runs when a request matches the decorator's path and method (Batman deciding how to respond).

**Introducing `async def`:**

FastAPI is built on modern Python features, notably `async` and `await`. Why? Performance!

Imagine Batman trying to handle multiple crimes simultaneously. If he had to fully resolve one situation (like a bank robbery) before starting the next (a breakout at Arkham), Gotham would be in chaos. `async def` allows our server to work like Batman *should*: when it encounters a task that involves waiting (like analyzing forensic data, waiting for Oracle's intel, or even just slow network I/O), it can *pause* that specific request and work on *other* incoming requests (other signals). When the waiting task is done, it seamlessly resumes the original request.

This makes FastAPI incredibly fast and efficient at handling many concurrent users, even when some operations take time.

*   **`async def`**: Declares an asynchronous function.
*   **`await`**: Used inside `async def` functions to pause execution while waiting for an asynchronous operation to complete (we'll see `await` more explicitly later).

For now, just know that you should generally define your FastAPI path operation functions with `async def`.

**Action:** Add the following to `main.py`:

```python
# main.py (continued)

# Step 3: Define the function that handles requests to "/"
# The '@app.get("/")' decorator links this function to GET requests for the root path.
@app.get("/")
async def read_root(): # Use 'async def' for asynchronous path operation functions
    # Step 4: Define what the function returns
    # FastAPI automatically converts Python dictionaries to JSON responses.
    return {"message": "Hello, Gotham!"}
```

## 6. The Case File: Returning Data (JSON)

Our `read_root` function returns a simple Python dictionary. FastAPI is smart enough to automatically convert this dictionary into **JSON** (JavaScript Object Notation), the standard data format for web APIs (like a standardized case file format).

## 7. Powering Up the Batcomputer: Running the Server

We have the gadget blueprint (`main.py`) and the power source (Uvicorn). Let's start the server!

**Action:**

*   Make sure you are in the `lesson_01` directory in your terminal (where `main.py` is).
*   Ensure your virtual environment (`venv`) is active.
*   Run the command: `uvicorn main:app --reload`
    *   `uvicorn`: The command to run the server.
    *   `main`: The Python file (`main.py`) where your FastAPI app lives.
    *   `app`: The object inside `main.py` that is the FastAPI instance (`app = FastAPI()`).
    *   `--reload`: This tells Uvicorn to automatically restart the server whenever you save changes to `main.py`. Super useful during development!

You should see output indicating the server is running, usually on `http://127.0.0.1:8000`.

**Action:**

*   Open your web browser and go to `http://127.0.0.1:8000`.
*   You should see: `{"message":"Hello, Gotham!"}`

Congratulations! You've lit your first Bat-Signal and received a response from your API!

## 8. The Crime Map: Using Interactive API Docs (`/docs`)

Batman needs maps and databases to track criminals. FastAPI gives you an amazing built-in crime map: automatic interactive API documentation.

**Action:**

*   Go to `http://127.0.0.1:8000/docs` in your browser.

You'll see a Swagger UI interface. This page:

*   Lists all your API endpoints (just `/` for now).
*   Shows the HTTP method (`GET`).
*   Allows you to expand the endpoint details.
*   Provides a "**Try it out**" button. Click it!
*   Then click the "**Execute**" button.

The interface will send a request to your running server *from the browser* and display the response (`{"message":"Hello, Gotham!"}`) right there! This is incredibly useful for testing and understanding your API without needing external tools yet. We will use `/docs` extensively throughout this course.

---

**Batman Analogy Recap:**

We used `FastAPI()` to create our API's *central console* (like the Batcomputer). We defined a *signal* (`@app.get("/")`) leading to an *efficient response protocol* (`async def read_root`) that returns a basic message from Gotham. Uvicorn is the *power source* running the operation, and `/docs` is our *interactive crime map* to navigate this system.

**Memory Aid:**

*   `FastAPI()` = Your Batcomputer Core
*   `@app.get("/path")` = Bat-Signal at `/path`
*   `async def function_name():` = Batman's Response Protocol (Efficient Function)
*   `return {}` = Message from Gotham
*   `uvicorn main:app --reload` = Power Up the Server (with Auto-Update)
*   `/docs` = Interactive Crime Map

---

**Homework:**

1.  Ensure you can successfully run the "Hello, Gotham!" app and view it in your browser at `/` and `/docs`.
2.  Experiment: Change the message returned by `read_root` in `main.py`. Save the file. Does the server restart automatically (thanks to `--reload`)? Refresh your browser at `/` to see the change.
3.  **Error Exploration:** Temporarily remove the `async` keyword from `async def read_root():` so it's just `def read_root():`. Save the file. Does Uvicorn show any warnings or errors in the terminal? Does the API still work at `/`? (FastAPI is often flexible with simple synchronous functions, but it's best practice to use `async def` for path operations). Add `async` back.
4.  Read: Briefly look up "What is JSON?" to understand the data format APIs commonly use (the standard format for our case files).

**Stretch Goal:**

Add a second endpoint to your `main.py`. Make it respond to `GET` requests at the path `/status`. This endpoint should return the JSON message `{"status": "Protecting Gotham"}`. Test it using both the browser directly (`http://127.0.0.1:8000/status`) and the `/docs` interface.

*(Find the complete code for this lesson, including the stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

If you were to deploy this app using Kubernetes, you'd first "containerize" it using Docker (packaging the app and its Python environment). Then, you'd tell Kubernetes to run this container inside a "Pod." The Pod is the smallest deployable unit in Kubernetes, essentially one or more containers running together. Think of the Pod as a mini Batcave, self-contained with everything needed for a specific mission (running your app instance).
