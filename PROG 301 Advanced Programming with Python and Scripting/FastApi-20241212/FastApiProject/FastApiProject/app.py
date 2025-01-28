from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates    #Template rendering engine for generating HTML responses
from pydantic import BaseModel                   #From Pydantic, used to define data models for input and output validation
import joblib                                   #Used to load a pre-trained machine learning model.
import numpy as np
from sklearn.datasets import load_iris
from pathlib import Path

# Load the trained model
model = joblib.load("iris_model.pkl")

# Initialize FastAPI
app = FastAPI()

# Set up templates directory path relative to app.py file
templates = Jinja2Templates(directory=r"E:\Academic\Courses\Jul-Dec 24\Advanced Python Programming\Lecture\FastApiProject\templates")

# Pydantic models for input and output data
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class IrisPrediction(BaseModel):
    predicted_class: int
    predicted_class_name: str

# Root page (renders index.html)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Prediction page (handles form submission)
@app.post("/predict", response_model=IrisPrediction)
async def predict(
    request: Request,
    sepal_length: float = Form(...),
    sepal_width: float = Form(...),
    petal_length: float = Form(...),
    petal_width: float = Form(...),
):
    # Convert the input data to a numpy array
    input_data = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

    # Make a prediction
    predicted_class = model.predict(input_data)[0]
    predicted_class_name = load_iris().target_names[predicted_class]

    # Return the result page with prediction details
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "predicted_class": predicted_class,
            "predicted_class_name": predicted_class_name,
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
        },
    )

# Health check endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "API is running"}

#use uvicorn app:app --reload to reload