from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image


DEFAULT_RANKS = (5, 15, 30, 60)
MAX_PROCESSING_SIDE = 360


@dataclass(frozen=True, slots=True)
class CompressionVariant:
    rank: int
    filename: str
    retained_values: int
    storage_percent: float
    compression_ratio: float
    mean_absolute_error: float
    rmse: float
    quality_score: float
    retained_energy_percent: float
    preview_matrix: list[list[int]]

    def to_dict(self) -> dict[str, object]:
        return {
            "rank": self.rank,
            "filename": self.filename,
            "retained_values": self.retained_values,
            "storage_percent": self.storage_percent,
            "compression_ratio": self.compression_ratio,
            "mean_absolute_error": self.mean_absolute_error,
            "rmse": self.rmse,
            "quality_score": self.quality_score,
            "retained_energy_percent": self.retained_energy_percent,
            "preview_matrix": self.preview_matrix,
        }


@dataclass(frozen=True, slots=True)
class CompressionResult:
    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    original_values: int
    max_rank: int
    singular_values: list[float]
    energy_curve: list[dict[str, float]]
    variants: list[CompressionVariant]

    @property
    def default_variant(self) -> CompressionVariant:
        return self.variants[min(1, len(self.variants) - 1)]

    def to_dict(self) -> dict[str, object]:
        return {
            "method": "SVD image compression",
            "formula": "A_k = U_k * Sigma_k * V_k^T",
            "original_width": self.original_width,
            "original_height": self.original_height,
            "processed_width": self.processed_width,
            "processed_height": self.processed_height,
            "original_values": self.original_values,
            "max_rank": self.max_rank,
            "singular_values": self.singular_values,
            "energy_curve": self.energy_curve,
            "variants": [variant.to_dict() for variant in self.variants],
            "default_variant": self.default_variant.to_dict(),
        }


def compress_image(
    image_path: str | Path,
    output_dir: str | Path,
    ranks: tuple[int, ...] = DEFAULT_RANKS,
) -> CompressionResult:
    source = Path(image_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as raw_image:
        grayscale = raw_image.convert("L")
        original_width, original_height = grayscale.size
        grayscale.thumbnail((MAX_PROCESSING_SIDE, MAX_PROCESSING_SIDE), Image.Resampling.LANCZOS)
        processed_width, processed_height = grayscale.size
        matrix = np.asarray(grayscale, dtype=np.float64)

    u, singular_values, vt = np.linalg.svd(matrix, full_matrices=False)
    max_rank = int(min(matrix.shape))
    chosen_ranks = _normalize_ranks(ranks, max_rank)
    total_energy = float(np.sum(singular_values**2)) or 1.0

    variants: list[CompressionVariant] = []
    prefix = f"compressed-{uuid4().hex[:8]}"
    for rank in chosen_ranks:
        reconstructed = _reconstruct(u, singular_values, vt, rank)
        clipped = np.clip(reconstructed, 0, 255).astype(np.uint8)
        filename = f"{prefix}-rank-{rank}.png"
        Image.fromarray(clipped, mode="L").save(output / filename)

        retained_values = rank * (processed_height + processed_width + 1)
        storage_percent = (retained_values / matrix.size) * 100
        compression_ratio = max(0.0, 1.0 - retained_values / matrix.size)
        difference = matrix - reconstructed
        mean_absolute_error = float(np.mean(np.abs(difference)))
        rmse = float(np.sqrt(np.mean(difference**2)))
        quality_score = max(0.0, 1.0 - rmse / 255.0)
        retained_energy = float(np.sum(singular_values[:rank] ** 2) / total_energy * 100)

        variants.append(
            CompressionVariant(
                rank=rank,
                filename=filename,
                retained_values=int(retained_values),
                storage_percent=round(storage_percent, 2),
                compression_ratio=round(compression_ratio, 4),
                mean_absolute_error=round(mean_absolute_error, 3),
                rmse=round(rmse, 3),
                quality_score=round(quality_score, 4),
                retained_energy_percent=round(retained_energy, 2),
                preview_matrix=_matrix_preview(clipped),
            )
        )

    return CompressionResult(
        original_width=original_width,
        original_height=original_height,
        processed_width=processed_width,
        processed_height=processed_height,
        original_values=int(matrix.size),
        max_rank=max_rank,
        singular_values=[round(float(value), 3) for value in singular_values[:12]],
        energy_curve=_energy_curve(singular_values, chosen_ranks, total_energy),
        variants=variants,
    )


def _normalize_ranks(ranks: tuple[int, ...], max_rank: int) -> list[int]:
    cleaned = sorted({rank for rank in ranks if 0 < rank <= max_rank})
    if not cleaned:
        cleaned = [max(1, min(max_rank, 10))]
    if max_rank not in cleaned and max_rank <= 80:
        cleaned.append(max_rank)
    return cleaned


def _reconstruct(
    u: np.ndarray,
    singular_values: np.ndarray,
    vt: np.ndarray,
    rank: int,
) -> np.ndarray:
    return (u[:, :rank] * singular_values[:rank]) @ vt[:rank, :]


def _matrix_preview(matrix: np.ndarray, size: int = 8) -> list[list[int]]:
    image = Image.fromarray(matrix.astype(np.uint8), mode="L")
    image = image.resize((size, size), Image.Resampling.BILINEAR)
    small = np.asarray(image, dtype=np.float64)
    return [[round(float(value) / 255.0 * 9) for value in row] for row in small]


def _energy_curve(
    singular_values: np.ndarray,
    ranks: list[int],
    total_energy: float,
) -> list[dict[str, float]]:
    curve: list[dict[str, float]] = []
    for rank in ranks:
        retained = float(np.sum(singular_values[:rank] ** 2) / total_energy * 100)
        curve.append({"rank": rank, "retained_energy_percent": round(retained, 2)})
    return curve
