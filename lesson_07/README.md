# Lesson 7: Alfred's Assistance - Background Tasks

**Recap:** In Lesson 6, we established Batcomputer Protocols (Dependency Injection) using `Depends` to reuse logic like pagination (`common_parameters`), manage resources like DB connections (`get_db_session`), and handle chained authentication/authorization (`get_api_key`, `verify_key_and_get_user`).

Now, we enlist **Alfred's Assistance**. Some tasks don't need to block Batman's immediate response. Sending notifications, generating complex reports, or logging activity can happen *after* the main request is finished. FastAPI provides `BackgroundTasks` to handle these "fire and forget" operations efficiently.

**Core Concepts:**

1.  **Background Tasks:** Operations performed after returning the HTTP response to the client.
2.  **Use Cases:** Sending emails/notifications, processing data, logging, tasks that don't affect the immediate response.
3.  **`BackgroundTasks` Object:** Injected into endpoints like dependencies.
4.  **`add_task` Method:** Used to schedule a function call to run in the background.
5.  **Passing Arguments:** Providing necessary data to the background task function.
6.  **Limitations:** Not suitable for tasks requiring immediate feedback or complex job queueing (use Celery, RQ, etc. for those).

---

## 1. Why Background Tasks?

Imagine logging every Batcomputer access. If logging takes 2 seconds, should Batman wait 2 seconds *every time* he accesses a file before getting the data? No! The logging can happen *after* the file data is returned.

Similarly, if requesting a complex intel report takes 10 seconds to compile, the API should immediately respond "Alfred is compiling the report..." and let Alfred do the work in the background.

## 2. Injecting `BackgroundTasks`

FastAPI provides a `BackgroundTasks` object that you can inject into your endpoint function signature, just like `Depends`.

**Action:**

*   Create `lesson_07` directory and copy `lesson_06/main.py` into it.
*   Open `lesson_07/main.py`.
*   Import `BackgroundTasks` from `fastapi`.
*   Import `time` and `os` for the simulation.

## 3. Defining the Background Task Function

This is a regular Python function (can be `def` or `async def`) that performs the background work.

**Action:** Define the `log_batcomputer_activity` function:

```python
# main.py (in lesson_07)
import time
import os

# ... (imports, models, app instance, dependencies ...)

# --- Background Task Functions (Alfred's Duties) ---

def log_batcomputer_activity(user_email: str, activity: str = ""):
    """ Simulates Alfred logging activity to the Batcomputer logs. """
    log_message = f"User {user_email} activity: {activity}\n"
    print(f"--- BACKGROUND TASK START: Logging activity: '{log_message.strip()}' ---")
    # Simulate work (e.g., writing to a file, network call)
    time.sleep(2)
    log_dir = "batcomputer_logs"
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "activity_log.txt")
    with open(file_path, mode="a") as log_file:
        log_file.write(log_message)
    print(f"--- BACKGROUND TASK END: Activity logged to '{file_path}' for {user_email} ---")

# ... (rest of the code)
```
This function simulates taking 2 seconds to write a log message to a file.

## 4. Adding Tasks with `background_tasks.add_task`

Inside your endpoint, after you have the necessary information, you call `background_tasks.add_task()` to schedule the function.

**Action:** Add the `/log-activity/{user_email}` endpoint:

```python
# main.py (in lesson_07)
from fastapi import BackgroundTasks # Make sure it's imported
from pydantic import EmailStr # For email validation in path

# ... (dependencies, background task functions ...)

# --- New Endpoints for Lesson 7 ---

@app.post("/log-activity/{user_email}")
async def log_user_activity(
    user_email: EmailStr, # Get email from path, validate format
    background_tasks: BackgroundTasks, # Inject BackgroundTasks
    activity_description: str = "Generic activity logged." # Optional query param
    ):
    """
    Logs user activity using a background task managed by Alfred.
    Returns a response immediately before the logging is complete.
    """
    confirmation_message = f"Activity logging initiated for {user_email}."
    print(f"Endpoint '/log-activity/{user_email}': Preparing background task.")

    # Schedule the task:
    background_tasks.add_task(
        log_batcomputer_activity, # The function Alfred should run
        user_email,               # 1st positional argument for the function
        activity=activity_description # Keyword argument for the function
    )
    # IMPORTANT: The task function (log_batcomputer_activity) will only run
    # *after* this endpoint function returns its response.

    print(f"Endpoint '/log-activity/{user_email}': Returning response.")
    # The response is sent back to the client immediately.
    return {"message": confirmation_message}

```
*   We inject `background_tasks: BackgroundTasks`.
*   We call `background_tasks.add_task()`, passing the function to run (`log_batcomputer_activity`) followed by any positional or keyword arguments it needs (`user_email`, `activity=activity_description`).
*   The endpoint returns the `confirmation_message` right away.
*   FastAPI then runs `log_batcomputer_activity` in the background.

## 5. Testing Background Tasks

**Action:**

1.  Run the server: `uvicorn main:app --reload`
2.  Go to `http://127.0.0.1:8000/docs`.
3.  Test the `POST /log-activity/{user_email}` endpoint. Provide an email (e.g., `bruce@wayne.enterprises`) and optionally an `activity_description` query parameter.
4.  **Observe:**
    *   You should get the `{"message": "Activity logging initiated..."}` response almost instantly in `/docs`.
    *   Watch the terminal where `uvicorn` is running. *After* the response is sent, you'll see the "BACKGROUND TASK START" message, then a pause (due to `time.sleep(2)`), and finally the "BACKGROUND TASK END" message.
    *   Check your project directory. A `batcomputer_logs` folder should appear containing `activity_log.txt` with the logged message.

This confirms the logging happened *after* the response was sent.

---

**Batman Analogy Recap:**

Alfred's Assistance (`BackgroundTasks`) allows offloading tasks that don't need immediate results. When Batman logs an activity (`POST /log-activity/...`), the API immediately confirms the request (`return {"message": ...}`). Alfred (`background_tasks.add_task(log_batcomputer_activity, ...)`), working diligently in the background, then performs the actual logging *after* Batman has already received his confirmation and moved on. This keeps the primary interaction fast and responsive.

**Memory Aid:**

*   `from fastapi import BackgroundTasks` = Get Alfred's Help
*   `def alfreds_task(arg1, kwarg1=None): ...` = Define Alfred's Duty (a function)
*   `async def endpoint(..., background_tasks: BackgroundTasks):` = Request Alfred's Assistance
*   `background_tasks.add_task(alfreds_task, arg1_val, kwarg1=kwarg1_val)` = Assign Duty to Alfred (runs after response)
*   Response is sent *before* Alfred finishes the task.

---

**Homework:**

1.  **Intel Report Model:** Create a Pydantic model `IntelReportRequest` with fields `recipient_email` (use `pydantic.EmailStr` for validation) and `report_name` (string, required).
2.  **Report Compilation Task:** Create a background task function `simulate_intel_report_compilation(report_request: IntelReportRequest)` that accepts an instance of your new model. Inside, print start/end messages including the report name and recipient email, and simulate work with `time.sleep(5)`.
3.  **Request Report Endpoint:** Create a `POST /request-intel-report` endpoint. It should accept a JSON body matching the `IntelReportRequest` model. Inject `BackgroundTasks` and use `add_task` to schedule your `simulate_intel_report_compilation` function, passing the received `report_request` object directly to it. Return an immediate confirmation message.
4.  **Test:** Use `/docs` to test `/request-intel-report`. Send a valid request body. Observe the immediate response and the delayed background task messages in the terminal. Try sending an invalid email format in the request body and observe the automatic 422 validation error from Pydantic's `EmailStr`.

**Stretch Goal:**

Modify the `log_batcomputer_activity` background task function. Make it check if the `batcomputer_logs/activity_log.txt` file exists. If it *doesn't* exist, print a message like "--- BACKGROUND TASK: Creating log file ---" before opening it in append mode (`"a"`). If it *does* exist, don't print the creation message. (Hint: Use `os.path.exists()`). This simulates initializing a resource only if needed within the background task.

*(Find the complete code for this lesson, including homework and stretch goal, in `main.py`)*

---

**Kubernetes Korner (Optional Context):**

While FastAPI `BackgroundTasks` run within the same process after the response, Kubernetes offers **Jobs** and **CronJobs** for more robust background processing.
*   **Job:** Runs one or more Pods to completion for a specific task (like a batch processing script). Kubernetes ensures the Job runs until a specified number of Pods successfully terminate.
*   **CronJob:** Creates Jobs on a repeating schedule (defined in cron format), suitable for periodic tasks like nightly backups or report generation.
These Kubernetes resources provide more resilience and scalability for background work compared to in-process tasks, especially for longer-running or critical operations.
