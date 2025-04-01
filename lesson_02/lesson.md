# Lesson 2: The Orb - Wielding Power with Path Parameters

**Recap:** In Lesson 1, we created our API's *space* using the Tesseract (`FastAPI()`) and opened our first *portal* (`@app.get("/")`). We learned about `async def` and how to run the server with Uvicorn. We also discovered the `/docs` map room!

Now, we seek the Orb containing the Power Stone. This stone grants immense power, often directed at specific targets. Similarly, **Path Parameters** allow our API to handle requests for *specific resources* identified directly within the URL path itself.

**Core Concepts:**

1.  **Path Parameters:** Making URLs dynamic (e.g., `/planets/Xandar`).
2.  **Defining Path Parameters:** Using `{}` in the route decorator.
3.  **Function Arguments:** Matching parameters in the function signature.
4.  **Type Hinting:** Specifying data types (`str`, `int`) for validation and clarity.
5.  **Using Parameters:** Accessing the values within your function.
6.  **Automatic Data Validation:** How FastAPI helps prevent errors.

---

## 1. What are Path Parameters?

Imagine you want an endpoint to get information about a specific planet. You could create separate endpoints like `/getXandarInfo`, `/getEarthInfo`, `/getVormirInfo`, but that's incredibly inefficient!

Path parameters let you create a *single* endpoint that can handle requests for *any* planet. The specific planet name becomes part of the URL path itself.

*   `http://127.0.0.1:8000/planets/Xandar`
*   `http://127.0.0.1:8000/planets/Earth`
*   `http://127.0.0.1:8000/planets/Knowhere`

Here, `Xandar`, `Earth`, and `Knowhere` are the values for a path parameter we might call `planet_name`.

## 2. Defining Path Parameters in FastAPI

You define path parameters directly in the route decorator string using curly braces `{}`.

**Action:**

*   Create a new directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_02`
*   Copy `main.py` from `lesson_01` into `lesson_02`. We'll build upon it.
    *   From the `fastapi-gauntlet-course` directory, you could run: `cp lesson_01/main.py lesson_02/`
*   Open `fastapi-gauntlet-course/lesson_02/main.py`.
*   Add the following endpoint:

```python
# main.py (in lesson_02)

# ... (keep the imports and app = FastAPI() instance) ...
# ... (keep the read_root and get_status endpoints from Lesson 1) ...

# New endpoint using a path parameter
@app.get("/planets/{planet_name}") # {planet_name} declares a path parameter
async def scan_planet(planet_name): # The function now expects an argument
    # We'll add type hinting next!
    return {"message": f"Scanning planet: {planet_name}"}

```

The `{planet_name}` in the path string tells FastAPI to expect *any* value in that segment of the URL and to capture it.

## 3. Connecting Path Parameters to Function Arguments

How does our Python code get the value (`Xandar`, `Earth`, etc.) from the URL? FastAPI passes it as an argument to the endpoint function.

Crucially, **the name inside the curly braces `{}` in the path *must match* the argument name in your function definition.**

In our example:

*   Path: `/planets/{planet_name}`
*   Function: `async def scan_planet(planet_name):` -> The names match!

## 4. The Power of Type Hinting

Okay, our function gets `planet_name`, but what *kind* of data is it? A string? A number? A boolean?

Python's **type hints** let us specify the expected data type. FastAPI uses these hints for several powerful things:

*   **Data Validation:** If you hint `planet_name: str`, FastAPI ensures the value received *can be interpreted* as a string (which is usually true for URL segments). If you hint `item_id: int`, FastAPI will try to convert the URL segment to an integer. If it fails (e.g., the path is `/items/abc`), FastAPI automatically returns a helpful HTTP error response (like `422 Unprocessable Entity`) *before your code even runs*! This saves you from writing lots of manual validation code.
*   **Editor Support:** Type hints give your code editor (like VS Code) information for better autocompletion and error checking.
*   **Automatic Documentation:** The `/docs` interface uses type hints to show what kind of data each parameter expects.

**Action:** Update the `scan_planet` function with a type hint:

```python
# main.py (in lesson_02, update scan_planet)

@app.get("/planets/{planet_name}")
async def scan_planet(planet_name: str): # Add the type hint ': str'
    return {"message": f"Scanning planet: {planet_name}"}
```

## 5. Using the Parameter Value

Inside the function, the path parameter (`planet_name` in our case) is just a regular Python variable holding the value extracted from the URL. You can use it like any other variable.

```python
# main.py (in lesson_02, example usage within scan_planet)

@app.get("/planets/{planet_name}")
async def scan_planet(planet_name: str):
    print(f"Received request for planet: {planet_name}") # Example: logging
    # Use an f-string to include the variable in the response
    return {"message": f"Scanning planet: {planet_name.capitalize()}"} # Example: capitalize it
```

## 6. Testing with Path Parameters

Let's see this in action!

**Action:**

1.  Make sure you are in the `lesson_02` directory.
2.  Activate your virtual environment if needed (`source ../lesson_01/venv/bin/activate` or similar, assuming you didn't create a new one for lesson_02).
3.  If you haven't already, install FastAPI: `pip install "fastapi[all]"` (only needed if you created a new venv).
4.  Run the server: `uvicorn main:app --reload`
5.  Go to `http://127.0.0.1:8000/docs`.
6.  You should now see the `/planets/{planet_name}` endpoint listed. Expand it.
7.  Notice how the documentation shows a required parameter `planet_name` of type `string`.
8.  Click "**Try it out**".
9.  Enter a planet name (e.g., `Xandar`) into the `planet_name` field.
10. Click "**Execute**".
11. Observe the response: `{"message":"Scanning planet: Xandar"}` (or `Xandar` if you added `.capitalize()`).
12. Try executing with different planet names (`Vormir`, `Titan`).
13. Now, try accessing it directly in the browser:
    *   `http://127.0.0.1:8000/planets/Asgard`
    *   `http://127.0.0.1:8000/planets/Sakaar`

---

**Thanos Analogy Recap:**

The Orb held the Power Stone, allowing focused power application. Path parameters (`/planets/{planet_name}`) give our API the *power* to handle requests for *specific* targets defined in the URL. Type hints (`planet_name: str`) ensure we're using the *correct form* of power (data type) and provide automatic validation, preventing misuse.

**Memory Aid:**

*   `{parameter_name}` in path = Target Specific Resource
*   `function(parameter_name: type)` = Receive & Validate Target Info
*   `/docs` = Your Power Stone testing range

---

**Homework:**

1.  Add a new endpoint `GET /stones/{stone_id}` to your `lesson_02/main.py`.
2.  This endpoint should accept an **integer** path parameter named `stone_id`. Use the correct type hint (`int`).
3.  The function should return a JSON response like: `{"stone_id": stone_id, "status": "Located"}`.
4.  Test this endpoint using `/docs`:
    *   Try valid IDs like `1`, `6`.
    *   Try an invalid ID like `mind`. What happens? Observe the automatic validation error FastAPI provides (likely a 422 status code with details about the expected type). This is FastAPI saving you work!
    *   Also test directly in the browser: `http://127.0.0.1:8000/stones/1` and `http://127.0.0.1:8000/stones/mind`.

**Stretch Goal:**

Create an endpoint `GET /alliances/{ally_name}/members/{member_id}`. This endpoint needs to accept *two* path parameters:
*   `ally_name` (should be a string)
*   `member_id` (should be an integer)
The function should return a JSON response containing both values, like: `{"alliance": ally_name, "member_id": member_id, "status": "Found"}`. Test it via `/docs`.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

When you want to manage multiple copies (replicas) of your application Pod for scalability or high availability, you use a Kubernetes object called a "Deployment." The Deployment ensures that the desired number of Pods matching your specification are running. If a Pod crashes, the Deployment automatically creates a new one to replace it, maintaining the desired state – like ensuring Thanos always has enough Outriders available.
