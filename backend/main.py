from fastapi import FastAPI
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from composition_analysis import (
    analyze_composition
)

from inference import predict_composition

app = FastAPI()
app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

@app.get("/")
def root():

    return {
        "message": "StructCompose API Running"
    }


@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...)
):

    # Read uploaded image
    contents = await file.read()

    # Convert bytes to numpy array
    np_arr = np.frombuffer(
        contents,
        np.uint8
    )

    # Decode image
    frame = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    # Run AI inference
    analysis = analyze_composition(
    frame
    )

    # Return embedding/features
    return analysis
