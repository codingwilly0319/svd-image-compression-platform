from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from compression_platform.platform import ImageCompressionPlatform


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        platform = ImageCompressionPlatform(temp / "records.json", temp / "uploads")
        record = platform.analyze_image(ROOT / "sample_images" / "sample-gradient.png")
        assert record.result_label.startswith("Rank")
        assert record.features["variants"]
        assert platform.history()
        summary = platform.admin_summary()
        assert summary["total_records"] == 1
    print("ALL FEATURES PASSED")


if __name__ == "__main__":
    main()
