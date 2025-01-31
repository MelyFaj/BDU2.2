from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from sklearn.datasets import load_iris

# Load the trained model
model = joblib.load("iris_model.pkl")

app = FastAPI()


class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class IrisPrediction(BaseModel):
    predicted_class: int
    predicted_class_name: str


@app.post("/predict", response_model=IrisPrediction)
def predict(data: IrisInput):
    # Convert the input data to a numpy array
    input_data = np.array(
        [[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]]
    )

    # Make a prediction
    predicted_class = model.predict(input_data)[0]
    predicted_class_name = load_iris().target_names[predicted_class]

    return IrisPrediction(
        predicted_class=predicted_class, predicted_class_name=predicted_class_name
    )

# Optional: Health Check Endpoint
@app.get("/")
def health_check():
    return {"status": "API is running"}
