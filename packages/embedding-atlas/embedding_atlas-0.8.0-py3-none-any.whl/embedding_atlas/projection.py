# Copyright (c) 2025 Apple Inc. Licensed under MIT License.

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .utils import Hasher, cache_path, logger


@dataclass
class Projection:
    # Array with shape (N, embedding_dim), the high-dimensional embedding
    projection: np.ndarray

    knn_indices: np.ndarray
    knn_distances: np.ndarray

    @staticmethod
    def exists(path: Path):
        return (
            path.with_suffix(".projection.npy").exists()
            and path.with_suffix(".knn_indices.npy").exists()
            and path.with_suffix(".knn_distances.npy").exists()
        )

    @staticmethod
    def save(path: Path, value: "Projection"):
        np.save(
            path.with_suffix(".projection.npy"),
            value.projection,
            allow_pickle=False,
        )
        np.save(
            path.with_suffix(".knn_indices.npy"),
            value.knn_indices,
            allow_pickle=False,
        )
        np.save(
            path.with_suffix(".knn_distances.npy"),
            value.knn_distances,
            allow_pickle=False,
        )

    @staticmethod
    def load(path: Path) -> "Projection":
        return Projection(
            projection=np.load(
                path.with_suffix(".projection.npy"),
                allow_pickle=False,
            ),
            knn_indices=np.load(
                path.with_suffix(".knn_indices.npy"),
                allow_pickle=False,
            ),
            knn_distances=np.load(
                path.with_suffix(".knn_distances.npy"),
                allow_pickle=False,
            ),
        )


def _run_umap(
    hidden_vectors: np.ndarray,
    umap_args: dict = {},
) -> Projection:
    logger.info("Running UMAP for input with shape %s...", str(hidden_vectors.shape))  # type: ignore

    import umap
    from umap.umap_ import nearest_neighbors

    metric = umap_args.get("metric", "cosine")
    n_neighbors = umap_args.get("n_neighbors", 15)

    knn = nearest_neighbors(
        hidden_vectors,
        n_neighbors=n_neighbors,
        metric=metric,
        metric_kwds=None,
        angular=False,
        random_state=None,
    )

    proj = umap.UMAP(**umap_args, precomputed_knn=knn)
    result: np.ndarray = proj.fit_transform(hidden_vectors)  # type: ignore

    return Projection(projection=result, knn_indices=knn[0], knn_distances=knn[1])


def _projection_for_texts(
    texts: list[str],
    model: str | None = None,
    trust_remote_code: bool = False,
    umap_args: dict = {},
) -> Projection:
    if model is None:
        model = "all-MiniLM-L6-v2"
    hasher = Hasher()
    hasher.update(
        {
            "version": 1,
            "texts": texts,
            "model": model,
            "umap_args": umap_args,
        }
    )
    digest = hasher.hexdigest()
    cpath = cache_path("projections") / digest

    if Projection.exists(cpath):
        logger.info("Using cached projection from %s", str(cpath))
        return Projection.load(cpath)

    # Import on demand.
    from sentence_transformers import SentenceTransformer

    logger.info("Loading model %s...", model)
    transformer = SentenceTransformer(model, trust_remote_code=trust_remote_code)

    logger.info("Running embedding for %d texts...", len(texts))
    hidden_vectors = transformer.encode(texts)

    result = _run_umap(hidden_vectors, umap_args)
    Projection.save(cpath, result)
    return result


def _projection_for_images(
    images: list,
    model: str | None = None,
    trust_remote_code: bool = False,
    umap_args: dict = {},
) -> Projection:
    if model is None:
        model = "google/vit-base-patch16-384"
    hasher = Hasher()
    hasher.update(
        {
            "version": 1,
            "images": images,
            "model": model,
            "umap_args": umap_args,
        }
    )
    digest = hasher.hexdigest()
    cpath = cache_path("projections") / (digest + ".npy")

    if Projection.exists(cpath):
        logger.info("Using cached projection from %s", str(cpath))
        return Projection.load(cpath)

    # Import on demand.
    from io import BytesIO

    import torch
    import tqdm
    from PIL import Image
    from transformers import pipeline

    def load_image(value):
        if isinstance(value, bytes):
            return Image.open(BytesIO(value)).convert("RGB")
        elif isinstance(value, dict) and "bytes" in value:
            return Image.open(BytesIO(value["bytes"])).convert("RGB")
        else:
            raise ValueError("invalid image value")

    logger.info("Loading model %s...", model)

    pipe = pipeline("image-feature-extraction", model=model, device_map="auto")

    logger.info("Running embedding for %d images...", len(images))
    tensors = []
    batch_size = 16

    current_batch = []

    @torch.no_grad()
    def process_batch():
        rs: torch.Tensor = pipe(current_batch, return_tensors=True)  # type: ignore
        current_batch.clear()
        for r in rs:
            if len(r.shape) == 3:
                r = r.mean(1)
            assert len(r.shape) == 2
            tensors.append(r)

    for image in tqdm.tqdm(images, smoothing=0.1):
        current_batch.append(load_image(image))
        if len(current_batch) >= batch_size:
            process_batch()
    process_batch()

    hidden_vectors = torch.concat(tensors).to(torch.float32).cpu().numpy()

    result = _run_umap(hidden_vectors, umap_args)
    Projection.save(cpath, result)
    return result


def compute_text_projection(
    data_frame: pd.DataFrame,
    text: str,
    x: str = "projection_x",
    y: str = "projection_y",
    neighbors: str | None = "neighbors",
    model: str | None = None,
    trust_remote_code: bool = False,
    umap_args: dict = {},
):
    """
    Compute text embeddings and generate 2D projections using UMAP.

    This function processes text data by creating embeddings using a SentenceTransformer
    model and then reducing the dimensionality to 2D coordinates using UMAP for
    visualization purposes.

    Args:
        data_frame: pandas DataFrame containing the text data to process.
        text: str, column name containing the texts to embed.
        x: str, column name where the UMAP X coordinates will be stored.
        y: str, column name where the UMAP Y coordinates will be stored.
        neighbors: str, column name where the nearest neighbor indices will be stored.
        model: str, name or path of the SentenceTransformer model to use for embedding.
        trust_remote_code: bool, whether to trust and execute remote code when loading
            the model from HuggingFace Hub. Default is False.
        umap_args: dict, additional keyword arguments to pass to the UMAP algorithm
            (e.g., n_neighbors, min_dist, metric).

    Returns:
        The input DataFrame with added columns for X, Y coordinates and nearest neighbors.
    """

    text_series = data_frame[text].astype(str).fillna("")
    proj = _projection_for_texts(
        list(text_series),
        model=model,
        trust_remote_code=trust_remote_code,
        umap_args=umap_args,
    )
    data_frame[x] = proj.projection[:, 0]
    data_frame[y] = proj.projection[:, 1]
    if neighbors is not None:
        data_frame[neighbors] = [
            {"distances": b, "ids": a}  # ID is always the same as the row index.
            for a, b in zip(proj.knn_indices, proj.knn_distances)
        ]


def compute_image_projection(
    data_frame: pd.DataFrame,
    image: str,
    x: str = "projection_x",
    y: str = "projection_y",
    neighbors: str | None = "neighbors",
    model: str | None = None,
    trust_remote_code: bool = False,
    umap_args: dict = {},
):
    """
    Compute image embeddings and generate 2D projections using UMAP.

    This function processes image data by creating embeddings using a model and
    then reducing the dimensionality to 2D coordinates using UMAP for
    visualization purposes.

    Args:
        data_frame: pandas DataFrame containing the image data to process.
        image: str, column name containing the images to embed.
        x: str, column name where the UMAP X coordinates will be stored.
        y: str, column name where the UMAP Y coordinates will be stored.
        neighbors: str, column name where the nearest neighbor indices will be stored.
        model: str, name or path of the model to use for embedding.
        trust_remote_code: bool, whether to trust and execute remote code when loading
            the model from HuggingFace Hub. Default is False.
        umap_args: dict, additional keyword arguments to pass to the UMAP algorithm
            (e.g., n_neighbors, min_dist, metric).

    Returns:
        The input DataFrame with added columns for X, Y coordinates and nearest neighbors.
    """

    image_series = data_frame[image]
    proj = _projection_for_images(
        list(image_series),
        model=model,
        trust_remote_code=trust_remote_code,
        umap_args=umap_args,
    )
    data_frame[x] = proj.projection[:, 0]
    data_frame[y] = proj.projection[:, 1]
    if neighbors is not None:
        data_frame[neighbors] = [
            {"distances": b, "ids": a}  # ID is always the same as the row index.
            for a, b in zip(proj.knn_indices, proj.knn_distances)
        ]
