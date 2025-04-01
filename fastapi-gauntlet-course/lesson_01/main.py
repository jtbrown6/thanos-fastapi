# Lesson 1: The Tesseract - Creating Your First API Space
# Complete code including Stretch Goal

# Step 1: Import the necessary class
from fastapi import FastAPI

# Step 2: Create an instance of the FastAPI class
# This 'app' object is the main point of interaction for creating your API.
app = FastAPI()

# Step 3: Define the function that handles requests to "/"
# The '@app.get("/")' decorator links this function to GET requests for the root path.
@app.get("/")
async def read_root(): # Use 'async def' for asynchronous path operation functions
    """
    The root endpoint of our API. Returns a welcome message.
    """
    # Step 4: Define what the function returns
    # FastAPI automatically converts Python dictionaries to JSON responses.
    return {"message": "Hello, Universe!"}

# Step 5 (Stretch Goal): Add another simple endpoint
@app.get("/status")
async def get_status():
    """
    Returns the current status of our quest.
    Accessible via GET request to /status
    """
    return {"status": "Seeking Stones"}

# To run this application:
# 1. Make sure you are in the 'lesson_01' directory in your terminal
# 2. Make sure your virtual environment is activated (`source venv/bin/activate` or `venv\Scripts\activate`)
# 3. Run: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000
# 5. Also check the interactive docs at http://127.0.0.1:8000/docs
