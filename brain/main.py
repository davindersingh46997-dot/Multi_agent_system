from fastapi import FastAPI
from pydantic import BaseModel
import base64
import cv2
import numpy as np


app = FastAPI()


class FrameRequest(BaseModel):
    frame: str


@app.post("/face/frame")
async def receive_frame(data: FrameRequest):

    # Remove the Base64 header
    image_data = data.frame.split(",")[1]

    # Decode Base64
    image_bytes = base64.b64decode(image_data)

    # Convert bytes to numpy array
    np_array = np.frombuffer(image_bytes, np.uint8)

    # Convert numpy array to OpenCV image
    frame = cv2.imdecode(
        np_array,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        return {
            "success": False,
            "message": "Could not decode frame"
        }

    # Show the frame
    cv2.imshow("Frontend Camera Frame", frame)

    cv2.waitKey(1)

    return {
        "success": True,
        "message": "Frame received"
    }