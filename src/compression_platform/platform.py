from __future__ import annotations

from pathlib import Path

from .compression import compress_image
from .records import CompressionRecord, RecordStore


class ImageCompressionPlatform:
    def __init__(self, record_path: str | Path, output_dir: str | Path) -> None:
        self.store = RecordStore(record_path)
        self.output_dir = Path(output_dir)

    def analyze_image(self, image_path: str | Path) -> CompressionRecord:
        result = compress_image(image_path, self.output_dir)
        default = result.default_variant
        return self.store.create_record(
            image_name=Path(image_path).name,
            result_label=f"Rank {default.rank}",
            quality_score=default.quality_score,
            variants=[variant.to_dict() for variant in result.variants],
            features=result.to_dict(),
        )

    def history(self) -> list[CompressionRecord]:
        return self.store.list_records()

    def admin_summary(self) -> dict[str, object]:
        return self.store.summary()

    def get_record(self, record_id: str) -> CompressionRecord:
        return self.store.get_record(record_id)

