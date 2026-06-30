from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compression_platform.records import RecordStore


class RecordStoreTest(unittest.TestCase):
    def test_create_and_summarize_compression_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = RecordStore(Path(directory) / "records.json")
            record = store.create_record(
                image_name="sample.png",
                result_label="Rank 15",
                quality_score=0.91,
                variants=[{"rank": 15, "compression_ratio": 0.7, "rmse": 8.5}],
                features={"default_variant": {"compression_ratio": 0.7, "rmse": 8.5}},
            )

            loaded = store.get_record(record.id)
            summary = store.summary()

        self.assertEqual("Rank 15", loaded.result_label)
        self.assertEqual(1, summary["total_records"])
        self.assertEqual(0.91, summary["average_quality_score"])
        self.assertEqual(0.7, summary["average_compression_ratio"])


if __name__ == "__main__":
    unittest.main()
