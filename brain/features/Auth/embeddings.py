import insightface
from insightface.app import FaceAnalysis

class FaceService:

    def __init__(self):

        self.app = FaceAnalysis(
            name="buffalo_sc",
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0, det_size=(320,320)
        )

    def get_embeddings(self,image):

        faces = self.app.get(image)

        if len(faces) == 0:
            return None

        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        face = faces[0]

        return face.normed_embedding
