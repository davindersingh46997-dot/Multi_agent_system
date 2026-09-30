from fastapi import FastAPI
from pydantic import BaseModel
import base64
from brain.api.Programming_api import router as programmer_router
from brain.api.auth_api import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from brain.database.session import engine,Base

app = FastAPI(
     title="Autonomous Coding Agent", 
     description="AI-powered autonomous programming agent", 
     version="1.0.0", 
    )

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/face/frame")
# async def receive_frame(data: FrameRequest):

#     # Remove the Base64 header
#     image_data = data.frame.split(",")[1]

#     # Decode Base64
#     image_bytes = base64.b64decode(image_data)

#     # Convert bytes to numpy array
#     np_array = np.frombuffer(image_bytes, np.uint8)

#     # Convert numpy array to OpenCV image
#     frame = cv2.imdecode(
#         np_array,
#         cv2.IMREAD_COLOR
#     )

#     if frame is None:
#         return {
#             "success": False,
#             "message": "Could not decode frame"
#         }

#     # Show the frame
#     cv2.imshow("Frontend Camera Frame", frame)

#     cv2.waitKey(1)

#     return {
#         "success": True,
#         "message": "Frame received"
#     }

app.include_router(
    programmer_router
)

app.include_router(
    auth_router,
    prefix="/api"
)