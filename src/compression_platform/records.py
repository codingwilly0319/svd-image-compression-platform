from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class CompressionRecord:
    id: str
    image_name: str
    result_label: str
    quality_score: float
    variants: list[dict[str, object]]
    features: dict[str, object]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def predicted_label(self) -> str:
        return self.result_label

    @property
    def confidence(self) -> float:
        return self.quality_score

    @property
    def status(self) -> str:
        return "processed"

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "image_name": self.image_name,
            "result_label": self.result_label,
            "quality_score": self.quality_score,
            "variants": self.variants,
            "features": self.features,
            "created_at": self.created_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CompressionRecord:
        return cls(
            id=str(data["id"]),
            image_name=str(data["image_name"]),
            result_label=str(data.get("result_label", data.get("predicted_label", "Rank unknown"))),
            quality_score=float(data.get("quality_score", data.get("confidence", 0.0))),
            variants=list(data.get("variants", data.get("predictions", []))),
            features=dict(data.get("features", {})),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat())),
        )



class RecordNotFoundError(ValueError):
    """Raised when a compression record cannot be found."""


class RecordStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def list_records(self) -> list[CompressionRecord]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [CompressionRecord.from_dict(item) for item in data.get("records", [])]

    def add_record(self, record: CompressionRecord) -> CompressionRecord:
        records = self.list_records()
        records.append(record)
        self._write(records)
        return record

    def create_record(
        self,
        image_name: str,
        result_label: str,
        quality_score: float,
        variants: list[dict[str, object]],
        features: dict[str, object],
    ) -> CompressionRecord:
        record = CompressionRecord(
            id=uuid4().hex[:8],
            image_name=image_name,
            result_label=result_label,
            quality_score=quality_score,
            variants=variants,
            features=features,
        )
        return self.add_record(record)

    def get_record(self, record_id: str) -> CompressionRecord:
        for record in self.list_records():
            if record.id == record_id:
                return record
        raise RecordNotFoundError(f"Record not found: {record_id}")

    def summary(self) -> dict[str, object]:
        records = self.list_records()
        total = len(records)
        average_quality = sum(record.quality_score for record in records) / total if total else 0.0

        compression_values = []
        error_values = []
        for record in records:
            default = record.features.get("default_variant", {})
            if isinstance(default, dict):
                compression_values.append(float(default.get("compression_ratio", 0.0)))
                error_values.append(float(default.get("rmse", 0.0)))

        average_compression = sum(compression_values) / total if total and compression_values else 0.0
        average_error = sum(error_values) / total if total and error_values else 0.0

        return {
            "total_records": total,
            "average_quality_score": round(average_quality, 4),
            "average_compression_ratio": round(average_compression, 4),
            "average_error": round(average_error, 3),
            "processed_records": total,
        }

    def _write(self, records: list[CompressionRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"records": [record.to_dict() for record in records]}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
