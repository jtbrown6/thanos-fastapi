# Lesson 8: The Batcave Display - Serving Static Assets & HTML Templates

**Recap:** In Lesson 7, we enlisted Alfred's Assistance (`BackgroundTasks`) to handle operations like logging (`log_batcomputer_activity`) or report compilation (`simulate_intel_report_compilation`) after the main response was sent, keeping the API responsive.

So far, our API primarily returns JSON data, which is great for programmatic clients but not very user-friendly for direct viewing in a browser. Now, we build the **Batcave Display** – a web interface. This involves serving static files (CSS, JavaScript, images) and rendering dynamic HTML content using templates.

**Core Concepts:**

1.  **Static Files:** Serving CSS, JavaScript, images, etc., directly from the server.
2.  **`StaticFiles`:** FastAPI's way to mount a directory for serving static assets.
3.  **HTML Templates:** Generating dynamic HTML pages based on data.
4.  **Jinja2:** A popular Python templating engine.
5.  **`Jinja2Templates`:** FastAPI's integration for using Jinja2.
6.  **`Request` Object:** Needed by templates to generate URLs (e.g., for static files).
7.  **Rendering Templates:** Using `templates.TemplateResponse` to return rendered HTML.
8.  **Passing Context:** Sending Python data (variables, dictionaries, lists) to the template for rendering.
9.  **`url_for`:** Jinja2 function (used with `Request`) to generate URLs for static files or other endpoints dynamically.

---

## 1. Serving Static Files (CSS, JS, Images)

Web pages need CSS for styling, JavaScript for interactivity, and images. These are "static" because they don't change per request. FastAPI needs to know where to find these files and how to serve them.

**Action:**

*   Create `lesson_08` directory and copy `lesson_07/main.py` into it.
*   Create two new subdirectories inside `lesson_08`: `static` and `templates`.
*   Create a simple CSS file `lesson_08/static/style.css` (you can copy the example from the final code or create your own).
*   In `lesson_08/main.py`, import `StaticFiles` and mount the directory:

```python
# main.py (in lesson_08)
from fastapi import FastAPI, Request # Import Request
from fastapi.staticfiles import StaticFiles # Import StaticFiles
# ... other imports ...

app = FastAPI()

# --- Mount Static Files Directory ---
# This line tells FastAPI: "Any request starting with '/static' should serve files
# from the directory named 'static' relative to where main.py is."
# The 'name="static"' allows us to refer to this mount point later using url_for.
app.mount("/static", StaticFiles(directory="static"), name="static")

# ... rest of the code ...
```
Now, if you run the app, accessing `http://127.0.0.1:8000/static/style.css` in your browser should show the CSS content.

## 2. Setting Up Jinja2 Templates

Jinja2 is a powerful engine that lets you write HTML files with placeholders and logic (loops, conditionals) that get filled in with data from your Python code.

**Action:**

*   Install Jinja2: `pip install Jinja2` (if not already installed via `fastapi[all]`).
*   In `lesson_08/main.py`, import `Jinja2Templates` and configure it:

```python
# main.py (in lesson_08)
from fastapi.templating import Jinja2Templates # Import Jinja2Templates
# ... other imports ...

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Configure Templates ---
# Tell Jinja2Templates where to find your HTML files.
templates = Jinja2Templates(directory="templates")

# ... rest of the code ...
```

## 3. Creating HTML Template Files

Now, let's create the actual HTML files within the `templates` directory.

**Action:**

*   Create `lesson_08/templates/index.html`.
*   Create `lesson_08/templates/contacts_list.html` (renamed from `character_list.html`).
*   Populate these files with HTML structure. Use Jinja2 syntax (`{{ variable }}` for displaying data, `{% for item in list %}` for loops, `{% if condition %}` for conditionals). See the final code for examples. Crucially, include the `request` object when calling `TemplateResponse` if you plan to use `url_for`.

**Example Snippet (`index.html`):**

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Link CSS using url_for - requires 'request' in context -->
    <link href="{{ request.url_for('static', path='/style.css') }}" rel="stylesheet">
    <title>{{ page_title }}</title> <!-- Variable from Python -->
</head>
<body>
    <h1>{{ heading }}</h1> <!-- Variable from Python -->

    <h2>Gadget Inventory:</h2>
    <ul>
        <!-- Loop through dictionary from Python -->
        {% for gadget_id, gadget_info in gadgets.items() %}
            <li>
                ID {{ gadget_id }}: <strong>{{ gadget_info.name }}</strong>
                <!-- Conditional based on data -->
                Status: {% if gadget_info.in_stock %}In Stock{% else %}Out of Stock{% endif %}
                 <!-- Generate URL to another endpoint -->
                (<a href="{{ request.url_for('get_gadget_details', gadget_id=gadget_id) }}">View API Details</a>)
            </li>
        {% else %}
            <li>No gadgets found.</li>
        {% endfor %}
    </ul>
    <p><a href="/contacts-view">View Contact Database</a></p>
</body>
</html>
```

## 4. Creating Endpoints to Render Templates

These endpoints will look similar to our API endpoints but will return an HTML response generated from a template.

**Action:**

*   In `lesson_08/main.py`, import `Request` from `fastapi` and `HTMLResponse` from `fastapi.responses`.
*   Add the `/batcave-display` endpoint:

```python
# main.py (in lesson_08)
from fastapi import Request
from fastapi.responses import HTMLResponse

# ... (app, mount, templates setup ...)
# ... (database simulation, models, etc.) ...

# --- HTML Rendering Endpoints for Lesson 8 ---

@app.get("/batcave-display", response_class=HTMLResponse) # Return HTML
async def read_batcave_display(request: Request): # Inject the Request object
    """ Serves the main Batcave display HTML page using Jinja2 templates. """
    # Prepare data to pass to the template
    stock_count = sum(1 for g in gadget_inventory_db.values() if g.get("in_stock"))
    total_gadgets = len(gadget_inventory_db)
    status_info = {"status": f"{stock_count}/{total_gadgets} gadget types in stock.", "gadgets_in_stock": stock_count}

    # The context dictionary contains data accessible within the template
    context = {
        "request": request, # MUST include request for url_for to work
        "page_title": "Batcave Main Display",
        "heading": "Welcome to the Batcave",
        "status_data": status_info,
        "gadgets": gadget_inventory_db # Pass the gadget data
    }
    # Return a TemplateResponse, specifying the template file and context
    return templates.TemplateResponse("index.html", context)

# Homework Endpoint (add this too)
@app.get("/contacts-view", response_class=HTMLResponse)
async def view_contacts(request: Request):
    """ Serves an HTML page listing contacts. """
    context = {
        "request": request,
        "page_title": "Contact Database",
        "heading": "Registered Contacts",
        "contacts": contacts_db # Pass the contacts data
    }
    return templates.TemplateResponse("contacts_list.html", context) # Use the renamed template
```
*   We use `@app.get(...)` as usual.
*   `response_class=HTMLResponse` explicitly tells FastAPI (and docs) that HTML is returned.
*   We inject `request: Request`. This is **required** if your template uses `url_for` (like linking to static files or other endpoints).
*   We gather data into a `context` dictionary. The keys of this dictionary become variable names inside the Jinja2 template.
*   `templates.TemplateResponse("template_name.html", context)` renders the specified template file using the provided context data and returns it as an HTML response.

## 5. Testing the Web Interface

**Action:**

1.  Ensure you have created the `static` and `templates` directories and the necessary files (`style.css`, `index.html`, `contacts_list.html`).
2.  Install necessary dependencies: `pip install Jinja2 email-validator` (if not already installed).
3.  Run the server: `uvicorn main:app --reload`
4.  Open your browser and navigate to:
    *   `http://127.0.0.1:8000/batcave-display`: You should see the rendered `index.html` page, styled by the CSS.
    *   `http://127.0.0.1:8000/static/style.css`: You should see the raw CSS content.
    *   (Optional: `POST` some data to `/contacts` via `/docs` first).
    *   `http://127.0.0.1:8000/contacts-view`: You should see the rendered contacts list.

---

**Batman Analogy Recap:**

The Batcave Display (`HTML Templates`) provides a visual interface. Static assets like the Bat-symbol graphic or interface styles (`StaticFiles` serving CSS/images) are served directly. Dynamic information like gadget status or contact lists is fetched by Python endpoints (`@app.get("/batcave-display")`) and injected into HTML blueprints (`Jinja2Templates`) using a context dictionary. The `Request` object is needed so the templates can correctly link to static assets (`url_for('static', ...)`). `TemplateResponse` is Alfred assembling the final view for Batman.

**Memory Aid:**

*   `app.mount("/static", StaticFiles(directory="static"), name="static")` = Define where static Bat-files (CSS, images) are stored.
*   `templates = Jinja2Templates(directory="templates")` = Tell Alfred where the HTML blueprints are.
*   `@app.get("/page", response_class=HTMLResponse)` = Define an endpoint that shows a display screen.
*   `async def endpoint(request: Request):` = Inject `Request` if using `url_for` in the template.
*   `context = {"request": request, "data": my_data}` = Prepare the info for the display.
*   `templates.TemplateResponse("blueprint.html", context)` = Alfred renders the blueprint with the data.
*   `{{ variable }}` in HTML = Placeholder for data from context.
*   `{% for ... %}` / `{% if ... %}` in HTML = Logic within the blueprint.
*   `request.url_for('static', path='/style.css')` = Correctly link to static files from HTML.

---

**Homework:**

1.  **Create `contacts_list.html`:** Create the `lesson_08/templates/contacts_list.html` template. It should:
    *   Include a link to the `style.css` file using `url_for`.
    *   Display the `page_title` and `heading` passed from the context.
    *   Loop through the `contacts` dictionary passed from the context.
    *   For each contact, display its ID, name, affiliation (or "Unknown"), and trust level.
    *   Include a link back to the `/batcave-display` page.
    *   Handle the case where the `contacts` dictionary is empty (show a message like "No contacts found...").
2.  **Populate and Test:** Make sure the `/contacts-view` endpoint in `main.py` uses `templates.TemplateResponse("contacts_list.html", context)`. Run the app. Use `/docs` to `POST` one or two contacts to the `/contacts` endpoint. Then, navigate to `/contacts-view` in your browser and verify the contacts are displayed correctly.

**Stretch Goal:**

In `index.html`, make the "Gadget Inventory" list link to the API detail page for each gadget.
*   Ensure the `@app.get("/gadgets/{gadget_id}")` endpoint in `main.py` has `name="get_gadget_details"` added to its decorator.
*   In the `index.html` template loop, add an `<a>` tag around "View API Details" (or similar text).
*   Set the `href` attribute using Jinja2's `url_for`: `href="{{ request.url_for('get_gadget_details', gadget_id=gadget_id) }}"`.
*   Test by clicking the links on the `/batcave-display` page. They should take you to the JSON response for that specific gadget (e.g., `/gadgets/1`).

*(Find the complete code for this lesson, including templates and static files, in the repository)*

---

**Kubernetes Korner (Optional Context):**

When deploying a web application like this to Kubernetes, you often use an **Ingress Controller** and **Ingress Resources**. An Ingress acts as an entry point to your cluster, routing external HTTP/S traffic to the correct internal Service (which points to your FastAPI Pods). You can configure Ingress rules based on hostnames or URL paths. For example, an Ingress could route `batcomputer.waynecorp.com/api` to your FastAPI Service and `batcomputer.waynecorp.com/` (or `/static`) to a different service/Pod optimized for serving static files (like Nginx), although FastAPI's `StaticFiles` is often sufficient for moderate load.
