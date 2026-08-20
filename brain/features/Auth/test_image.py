import cv2
import numpy as np
from insightface.app import FaceAnalysis
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "buffalo_sc"
CAMERA_INDEX = 0

REQUIRED_SAMPLES = 10

STORAGE_DIR = Path("face_data")
EMBEDDING_FILE = STORAGE_DIR / "face_embedding.npy"


# ============================================================
# Create storage directory
# ============================================================

STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Initialize InsightFace
# ============================================================

app = FaceAnalysis(
    name=MODEL_NAME,
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(320, 320)
)


# ============================================================
# Start webcam
# ============================================================

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    raise RuntimeError("Could not open camera")


embeddings = []


print("========================================")
print("        FACE ENROLLMENT")
print("========================================")
print()
print("Look directly at the camera.")
print("Keep only one face visible.")
print()
print("Press Q to cancel.")
print()


# ============================================================
# Capture frames
# ============================================================

while len(embeddings) < REQUIRED_SAMPLES:

    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        continue

    # --------------------------------------------------------
    # Get faces from current frame
    # --------------------------------------------------------

    faces = app.get(frame)

    # --------------------------------------------------------
    # No face
    # --------------------------------------------------------

    if len(faces) == 0:

        cv2.putText(
            frame,
            "No face detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # --------------------------------------------------------
    # Multiple faces
    # --------------------------------------------------------

    elif len(faces) > 1:

        cv2.putText(
            frame,
            "Multiple faces detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # --------------------------------------------------------
    # Exactly one face
    # --------------------------------------------------------

    else:

        face = faces[0]

        embedding = face.normed_embedding

        embeddings.append(embedding.copy())

        cv2.putText(
            frame,
            f"Sample: {len(embeddings)}/{REQUIRED_SAMPLES}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    # --------------------------------------------------------
    # Show camera
    # --------------------------------------------------------

    cv2.imshow("Face Enrollment", frame)

    # --------------------------------------------------------
    # Quit
    # --------------------------------------------------------

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        print("Enrollment cancelled.")
        camera.release()
        cv2.destroyAllWindows()
        exit()


# ============================================================
# Stop camera
# ============================================================

camera.release()
cv2.destroyAllWindows()


# ============================================================
# Convert embeddings to NumPy array
# ============================================================

embeddings = np.array(embeddings)

print()
print("Captured embeddings shape:", embeddings.shape)


# ============================================================
# Average the embeddings
# ============================================================

mean_embedding = np.mean(
    embeddings,
    axis=0
)


# ============================================================
# Normalize the final embedding
# ============================================================

norm = np.linalg.norm(mean_embedding)

if norm == 0:
    raise RuntimeError("Invalid embedding generated.")

mean_embedding = mean_embedding / norm


# ============================================================
# Store embedding
# ============================================================

np.save(
    EMBEDDING_FILE,
    mean_embedding
)


# ============================================================
# Verification
# ============================================================

print()
print("========================================")
print("       ENROLLMENT SUCCESSFUL")
print("========================================")
print()
print("Embedding shape:", mean_embedding.shape)
print("Stored at:", EMBEDDING_FILE)
print()
print("First 10 values:")
print(mean_embedding[:10])