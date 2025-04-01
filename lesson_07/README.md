# Lesson 7: Sanctuary II - Background Operations

**Recap:** In Lesson 6, we explored the Mind Stone's influence through Dependency Injection (`Depends`), allowing us to reuse logic, manage resources (`yield`), and build complex validation chains.

Now, picture Thanos aboard his command ship, Sanctuary II. He gives an order (like "Send the Black Order to Earth"), and the ship confirms ("Acknowledged"), but the actual mission continues long after that initial command. Similarly, sometimes our API needs to perform an action triggered by a request, but that action might take time (like sending an email, processing an image, or generating a complex report). We don't want the user waiting for that long task to finish before getting a response. This is where **Background Tasks** come in.

**Core Concepts:**

1.  **The Problem:** Long-running operations blocking the response.
2.  **The Solution:** `BackgroundTasks` to run code *after* the response is sent.
3.  **Importing `BackgroundTasks`**.
4.  **Injecting `BackgroundTasks`:** Using dependency injection.
5.  **Adding Tasks:** `background_tasks.add_task(func, arg1, kwarg1=...)`.
6.  **Execution Flow:** Response first, task later.

---

## 1. The Problem: Blocking Operations

Imagine an endpoint `/send-report/{email}`. When called, it needs to:
1.  Generate a potentially large report (takes 10 seconds).
2.  Send the report via email (takes 5 seconds).
3.  Return a confirmation message to the user.

If we do this sequentially within the endpoint function:

```python
# DON'T DO THIS FOR LONG TASKS
@app.post("/send-report-blocking/{email}")
async def send_report_blocking(email: str):
    print(f"Generating report for {email}...")
    time.sleep(10) # Simulate long report generation
    print("Report generated. Sending email...")
    time.sleep(5) # Simulate sending email
    print("Email sent.")
    return {"message": f"Report sent to {email}"}
```
*(Requires `import time`)*

The user who called this endpoint would have to wait the *full 15 seconds* before receiving the `{"message": "Report sent..."}` response. This is a terrible user experience! The client might time out, or the user might just get frustrated.

## 2. The Solution: `BackgroundTasks`

FastAPI provides a `BackgroundTasks` utility that allows you to add functions to be run *after* the response has been sent.

**How it works:**

1.  Your endpoint receives the request.
2.  It performs any quick validation or setup.
3.  It adds the long-running function (e.g., `generate_and_send_report`) to the `BackgroundTasks` object.
4.  The endpoint immediately returns a response to the client (e.g., `{"message": "Report generation started..."}`).
5.  *After* the response is sent, FastAPI executes the functions added as background tasks.

This way, the user gets an immediate confirmation, and the heavy lifting happens behind the scenes, just like the Black Order carrying out their mission after Thanos gives the command.

## 3. Importing `BackgroundTasks`

It's a class provided directly by FastAPI.

```python
from fastapi import BackgroundTasks
```

## 4. Injecting `BackgroundTasks`

How does our endpoint function get access to the background task runner? Via Dependency Injection, of course! You declare a parameter in your endpoint function with a type hint of `BackgroundTasks`.

```python
async def my_endpoint(background_tasks: BackgroundTasks, ...):
    # ... endpoint logic ...
```
FastAPI will automatically create an instance of `BackgroundTasks` and pass it to your function.

## 5. Adding Tasks: `background_tasks.add_task()`

Once you have the `background_tasks` object, you use its `add_task` method.

`background_tasks.add_task(func, *args, **kwargs)`

*   `func`: The function you want to run in the background. **Important:** This should be a regular function (`def`) or an async function (`async def`).
*   `*args`: Any positional arguments that `func` needs.
*   `**kwargs`: Any keyword arguments that `func` needs.

**Action:**

*   Create the directory for this lesson: `mkdir fastapi-gauntlet-course/lesson_07`
*   Copy `main.py` from `lesson_06` into `lesson_07`: `cp lesson_06/main.py lesson_07/`
*   Open `fastapi-gauntlet-course/lesson_07/main.py`.
*   Import `BackgroundTasks` from `fastapi`.
*   Add a helper function to simulate writing to a log and the new endpoint:

```python
# main.py (in lesson_07)
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks # Import BackgroundTasks
import httpx
from pydantic import BaseModel
import time # Import time for simulation

# ... (keep app instance, models, databases, dependencies from lesson 6) ...

# --- Helper function for Background Task ---
def write_notification_log(email: str, message: str = ""):
    """ Simulates writing a log message to a file. """
    log_message = f"Notification for {email}: {message}\n"
    print(f"--- BACKGROUND TASK START: Writing log: '{log_message.strip()}' ---")
    # Simulate I/O delay
    time.sleep(3) 
    with open("notification_log.txt", mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Log written for {email} ---")


# --- New Endpoint Using BackgroundTasks ---
@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks # Inject BackgroundTasks
    ):
    """
    Sends a hypothetical notification and logs it in the background.
    Returns a response immediately.
    """
    confirmation_message = f"Notification queued for {email}"
    print(f"Endpoint '/send-notification/{email}': Preparing background task.")
    
    # Add the task to be run after the response is sent
    background_tasks.add_task(
        write_notification_log, # The function to call
        email, # First positional argument for the function
        message=confirmation_message # Keyword argument for the function
    )
    
    print(f"Endpoint '/send-notification/{email}': Returning response.")
    # The response is returned BEFORE write_notification_log fully executes
    return {"message": confirmation_message}

# ... (keep other endpoints) ...
```

**Explanation:**

1.  We import `BackgroundTasks` and `time`.
2.  We define `write_notification_log` which simulates a slow task (writing to a file with a `time.sleep`).
3.  The `/send-notification/{email}` endpoint takes the `email` path parameter and injects `background_tasks: BackgroundTasks`.
4.  `background_tasks.add_task(write_notification_log, email, message=confirmation_message)` schedules the `write_notification_log` function to run later, passing the `email` and `confirmation_message` as arguments.
5.  The endpoint immediately returns the `{"message": ...}` response.

## 6. Observing the Execution Flow

**Action:**

1.  Make sure you are in the `lesson_07` directory.
2.  Activate your virtual environment.
3.  Run the server: `uvicorn main:app --reload`
4.  Go to `http://127.0.0.1:8000/docs`.
5.  Find the `POST /send-notification/{email}` endpoint. Expand it.
6.  Click "**Try it out**". Enter an email address (e.g., `thanos@titan.net`).
7.  Click "**Execute**".
8.  **Observe Carefully:**
    *   You should get the `200 OK` response in `/docs` almost *immediately*.
    *   Watch the terminal where Uvicorn is running. You'll see the endpoint's print statements ("Preparing background task", "Returning response").
    *   *After* the response is returned, you will see the "BACKGROUND TASK START" message, then a pause (due to `time.sleep`), and finally the "BACKGROUND TASK END" message.
    *   Check your `lesson_07` directory. A file named `notification_log.txt` should have been created (or appended to) containing the log message.

This demonstrates that the response was sent *before* the background task completed its work.

---

**Thanos Analogy Recap:**

Sanctuary II receives Thanos' command (`POST /send-notification/...`). The bridge confirms immediately (`return {"message": ...}`). Then, *after* the confirmation, the ship's systems execute the actual long-running task (`background_tasks.add_task(write_notification_log, ...)`), like launching the Black Order or firing the cannons, without making Thanos wait for the entire operation to complete before knowing the command was received.

**Memory Aid:**

*   `BackgroundTasks` = Sanctuary II's Operations Deck
*   `background_tasks: BackgroundTasks` = Get Access to Ops Deck
*   `add_task(func, ...)` = Launch Mission (after confirming order)
*   Response Returns First = Thanos gets confirmation immediately.
*   Task Runs Later = Mission proceeds independently.

---

**Homework:**

1.  Create a Pydantic model `ReportRequest` with fields `recipient_email: str` and `report_name: str`.
2.  Create a `POST /generate-report` endpoint that accepts a `ReportRequest` object in the request body.
3.  Inject `BackgroundTasks`.
4.  Create a background task function `simulate_report_generation(email: str, name: str)` that prints a start message, sleeps for 5 seconds, and prints an end message including the email and report name.
5.  Add this function as a background task using data from the `ReportRequest` object.
6.  The endpoint should immediately return `{"message": f"Report '{report_request.report_name}' generation started for {report_request.recipient_email}."}`.
7.  Test using `/docs`.

**Stretch Goal:**

Modify the background task function `simulate_report_generation` to accept the entire `ReportRequest` Pydantic model instance as an argument instead of individual fields. Update the `add_task` call accordingly. Inside the background task function, access the data using `report_request.recipient_email` and `report_request.report_name`.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

While FastAPI's `BackgroundTasks` are great for tasks tied to a specific request that can run after the response, what about tasks that need to run independently, perhaps on a schedule, or ensure completion even if the original API Pod dies? Kubernetes offers:
*   **Jobs:** Define a task that runs one or more Pods until a specified number of them complete successfully. Ideal for batch processing, data migration, or one-off computations.
*   **CronJobs:** Define a Job that runs on a repeating schedule (like a cron schedule). Perfect for nightly reports, backups, or periodic cleanup tasks.
These Kubernetes objects manage task execution at the infrastructure level, providing more robustness and scheduling capabilities than in-process background tasks. Think of Jobs as specific missions launched by Sanctuary II, and CronJobs as its regularly scheduled patrols or maintenance routines.
