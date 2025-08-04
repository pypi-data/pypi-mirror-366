from typing import override
import numpy as np
from PIL import Image
from photos_drive.shared.llm.models.image_embeddings import ImageEmbeddings

DIMENSION = 100

FAKE_EMBEDDING = np.zeros((DIMENSION), dtype=np.float32)


class FakeImageEmbedder(ImageEmbeddings):
    @override
    def get_embedding_dimension(self) -> int:
        return DIMENSION

    @override
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        return np.vstack([FAKE_EMBEDDING for _ in texts])

    @override
    def embed_images(self, images: list[Image.Image]) -> np.ndarray:
        return np.vstack([FAKE_EMBEDDING for _ in images])
