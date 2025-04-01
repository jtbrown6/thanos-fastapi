# Lesson 8: Knowhere - Serving Static Assets & Templates

**Recap:** Aboard Sanctuary II in Lesson 7, we learned how to use `BackgroundTasks` to perform long-running operations without blocking the user's response, ensuring a smoother experience.

Our journey takes us to Knowhere, the massive severed head of a Celestial, now a mining colony and hub, famously housing the Collector's museum – a repository of unique artifacts and assets. Similarly, our web applications often need to serve static files (CSS stylesheets, JavaScript code, images – the visual *assets*) and render dynamic HTML pages (the *structure* displaying information) rather than just returning raw JSON data.

**Core Concepts:**

1.  **Serving Static Files:** Making CSS, JS, and images accessible via URLs.
2.  **`StaticFiles`:** FastAPI's way to mount a directory for static assets.
3.  **HTML Templates:** Generating HTML dynamically on the server.
4.  **Jinja2:** A popular templating engine for Python.
5.  **`Jinja2Templates`:** FastAPI's integration for rendering Jinja2 templates.
6.  **Rendering Templates:** Passing data from Python to HTML.
7.  **Linking Static Files in HTML:** Using `url_for`.

---

## 1. Beyond JSON: Serving Static Files

So far, our API has only returned JSON data. But web applications need more – stylesheets (CSS) to define appearance, JavaScript (JS) for interactivity, and images. These files don't change based on user input; they are *static*. We need a way for the browser to request these files directly from our server.

## 2. Mounting Static Files with `StaticFiles`

FastAPI provides the `StaticFiles` class to "mount" a directory. Mounting means making the contents of a specific directory on your server accessible under a specific URL path.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_08`
*   Copy `main.py` from `lesson_07` into `lesson_08`: `cp lesson_07/main.py lesson_08/`
*   Inside `lesson_08`, create a directory named `static`: `mkdir fastapi-gauntlet-course/lesson_08/static`
*   Inside `static`, create a simple CSS file named `style.css`:

    ```css
    /* static/style.css */
    body {
        font-family: sans-serif;
        background-color: #1a1a2e; /* Dark space blue */
        color: #e0e0e0; /* Light grey text */
        margin: 2em;
    }

    h1 {
        color: #f0c419; /* Gold */
        border-bottom: 2px solid #f0c419;
        padding-bottom: 5px;
    }

    .container {
        background-color: #2a2a3e;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    a {
        color: #a0c4ff; /* Light blue links */
    }
    ```
*   Now, open `fastapi-gauntlet-course/lesson_08/main.py`.
*   Import `StaticFiles` and mount the `static` directory:

```python
# main.py (in lesson_08)
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.staticfiles import StaticFiles # Import StaticFiles
# ... other imports ...

app = FastAPI()

# --- Mount Static Files Directory ---
# This line tells FastAPI to serve files from the 'static' directory
# when a request comes in for a path starting with '/static'.
# The 'name="static"' allows us to refer to this mount point later (e.g., in templates).
app.mount("/static", StaticFiles(directory="static"), name="static")

# ... (keep models, databases, dependencies, other endpoints) ...
```

**Explanation:**

*   `app.mount("/static", ...)`: Makes files accessible under the `/static` URL path.
*   `StaticFiles(directory="static")`: Specifies that the files are located in the directory named `static` relative to where you run `uvicorn`.
*   `name="static"`: Gives this static file mount a name, which is useful for generating URLs within templates.

**Action:**

1.  Run `uvicorn main:app --reload` from the `lesson_08` directory.
2.  Open your browser and go to `http://127.0.0.1:8000/static/style.css`.
3.  You should see the raw content of your `style.css` file! FastAPI is now serving it.

## 3. Dynamic Views: HTML Templates

Returning JSON is great for programmatic clients, but humans usually prefer nicely formatted HTML pages. We often need to generate this HTML *dynamically*, inserting data from our application (like user details, lists of items, etc.). This is where templating engines come in.

## 4. Jinja2: The Templating Engine

Jinja2 is a very popular and powerful templating engine for Python. It allows you to write HTML files with special placeholders and logic (like loops and conditionals) that get processed on the server before the final HTML is sent to the browser.

**Action:** Install Jinja2 (it might already be installed if you used `fastapi[all]`):

*   Run: `pip install Jinja2`

## 5. Integrating Jinja2 with `Jinja2Templates`

FastAPI provides `Jinja2Templates` to easily integrate Jinja2.

**Action:**

*   Inside `lesson_08`, create a directory named `templates`: `mkdir fastapi-gauntlet-course/lesson_08/templates`
*   Inside `templates`, create a file named `index.html`:

    ```html
    <!-- templates/index.html -->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Link to our static CSS file using url_for -->
        <link href="{{ url_for('static', path='/style.css') }}" rel="stylesheet">
        <!-- Use data passed from Python for the title -->
        <title>{{ page_title }} - FastAPI Gauntlet</title>
    </head>
    <body>
        <div class="container">
            <!-- Display the main heading passed from Python -->
            <h1>{{ heading }}</h1>
            
            <p>Welcome to the Knowhere Data Hub.</p>
            
            <!-- Example of using data passed in a dictionary -->
            <h2>Current Status:</h2>
            <ul>
                <li>Stones Acquired: {{ status_data.stones_acquired }}</li>
                <li>Quest Status: {{ status_data.status }}</li>
            </ul>

            <!-- Example of looping through a list passed from Python -->
            <h2>Known Stones:</h2>
            <ul>
                {% for stone_id, stone_info in stones.items() %}
                    <li>ID {{ stone_id }}: {{ stone_info.name }} ({{ stone_info.color }}) - Location: {{ stone_info.location }}</li>
                {% else %}
                    <li>No stones found in the database.</li>
                {% endfor %}
            </ul>

            <p><a href="/docs">Explore the API Docs</a></p>
        </div>
    </body>
    </html>
    ```
    *   **Key Jinja2 Syntax:**
        *   `{{ variable_name }}`: Prints the value of a variable passed from Python.
        *   `{% for item in list %}` ... `{% endfor %}`: Loops through items in a list/dict.
        *   `url_for('static', path='/style.css')`: Generates the correct URL for our static CSS file (uses the `name="static"` we set earlier). **Crucial for linking static assets!**

*   Now, open `fastapi-gauntlet-course/lesson_08/main.py`.
*   Import `Jinja2Templates` and `Request`. Configure the templates:

```python
# main.py (in lesson_08)
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request # Import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates # Import Jinja2Templates
# ... other imports ...

app = FastAPI()

# Mount Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Configure Templates ---
# Tell Jinja2Templates where to find the template files
templates = Jinja2Templates(directory="templates")

# ... (keep models, databases, dependencies, other endpoints) ...
```

## 6. Rendering Templates in Endpoints

To render a template, you need:
1.  The `Request` object (FastAPI injects this automatically if you type-hint it). Jinja2Templates needs it for context, especially for functions like `url_for`.
2.  The name of the template file (e.g., `"index.html"`).
3.  A dictionary containing the data you want to pass to the template. The keys of this dictionary become variable names inside the template. **Crucially, this dictionary *must* include a key named `"request"` with the `Request` object as its value.**

**Action:** Add an endpoint to render `index.html`:

```python
# main.py (in lesson_08, add new endpoint)

# ... (app, static mount, templates config, models, DBs, dependencies...)

# --- New Endpoint to Render HTML Template ---
@app.get("/home") # Use @app.get, not @app.get("/") if you have a root endpoint already
async def read_home(request: Request): # Inject the Request object
    """ Serves the main HTML page using Jinja2 templates. """
    
    # Prepare data to pass to the template
    # Get status data (reuse logic from /status endpoint if desired)
    acquired_count = sum(1 for stone in known_stones_db.values() if stone.get("acquired"))
    status_text = "All stones acquired!" if acquired_count == 6 else f"Seeking {6 - acquired_count} more stones..."
    status_info = {"status": status_text, "stones_acquired": acquired_count}

    context = {
        "request": request, # MUST include the request object
        "page_title": "Knowhere Hub", # Data for {{ page_title }}
        "heading": "Welcome to the Collector's Archive!", # Data for {{ heading }}
        "status_data": status_info, # Pass the status dictionary
        "stones": known_stones_db # Pass the entire stones database
    }
    
    # Render the template
    # templates.TemplateResponse(template_name, context_dictionary)
    return templates.TemplateResponse("index.html", context)

# ... (keep other endpoints) ...
```

## 7. Testing the HTML Page

**Action:**

1.  Run `uvicorn main:app --reload` from the `lesson_08` directory.
2.  Open your browser and go to `http://127.0.0.1:8000/home`.
3.  You should see your rendered HTML page!
    *   It should have the dark background and gold heading defined in `style.css`.
    *   The title and heading should match the data passed in the `context`.
    *   The status and list of stones should be dynamically generated based on the `known_stones_db` dictionary.
    *   View the page source in your browser – you'll see plain HTML, with the Jinja2 placeholders replaced by data. Check that the `<link>` tag for the CSS has the correct `/static/style.css` path generated by `url_for`.

---

**Thanos Analogy Recap:**

Knowhere served as a repository for assets and information. Our `static` directory holds the visual *assets* (CSS). The `templates` directory holds the *blueprints* (HTML structure with Jinja2 placeholders). `StaticFiles` makes the assets directly accessible, while `Jinja2Templates` takes a blueprint (`index.html`) and fills it with dynamic *information* (data from Python context) before presenting the final view (`TemplateResponse`). `url_for` ensures our blueprints correctly link to the stored assets.

**Memory Aid:**

*   `static/` directory = The Collector's Vault (for CSS, JS, images)
*   `app.mount("/static", StaticFiles(...))` = Open the Vault Door at `/static`
*   `templates/` directory = Blueprint Archive
*   `Jinja2Templates(directory="templates")` = Access the Archive
*   `TemplateResponse("file.html", {"request": req, ...})` = Build from Blueprint using Data
*   `{{ variable }}` = Placeholder for Data in Blueprint
*   `url_for('static', ...)` = Get Correct Path to Asset in Vault

---

**Homework:**

1.  Create a new template file `templates/character_list.html`.
2.  This template should display a heading "Characters Database" and an unordered list (`<ul>`).
3.  Inside the list, loop through a `characters` variable (which will be a dictionary passed from Python, like `characters_db`). For each character ID and character data, display their name and affiliation (e.g., `<li>ID 1: Thanos (Black Order)</li>`).
4.  Create a new endpoint `GET /characters-view` that:
    *   Injects the `Request` object.
    *   Renders the `character_list.html` template.
    *   Passes the `characters_db` dictionary (from Lesson 5/6) to the template under the key `"characters"`. Remember to include the `"request": request` key-value pair in the context dictionary.
5.  Link your `style.css` in the `<head>` of `character_list.html` using `url_for`.
6.  Test by navigating to `/characters-view` in your browser. (You might need to POST a character first using the `/characters` endpoint from Lesson 5 via `/docs` if `characters_db` is empty).

**Stretch Goal:**

In `templates/index.html`, add a link for each listed stone that goes to `/stones/{stone_id}` (e.g., `<a href="/stones/{{ stone_id }}">Details</a>`). Can you make this link generation dynamic using `url_for` within the template? (Hint: You might need to give your `/stones/{stone_id}` endpoint a `name` in its decorator, like `@app.get("/stones/{stone_id}", name="get_stone_details")`, and then use `url_for('get_stone_details', stone_id=stone_id)` in the template).

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`, `templates/index.html`, `templates/character_list.html`, and `static/style.css`)*

---

**Kubernetes Korner (Optional Context):**

How do you efficiently serve static files in a production Kubernetes environment? While FastAPI *can* serve them, it's often more efficient to let a dedicated web server like Nginx or a cloud provider's Content Delivery Network (CDN) handle them. In Kubernetes, you might configure an "Ingress" controller (like Nginx Ingress) to route requests for `/static/*` directly to a Pod serving those files (or even an external CDN), while requests for `/home` or `/api/*` go to your FastAPI application Pods. This offloads the work of serving static assets from your Python application.
