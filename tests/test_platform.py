from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import numpy  # noqa: F401
except ImportError:
    numpy = None

from compression_platform.platform import ImageCompressionPlatform


@unittest.skipIf(numpy is None, "NumPy is required for compression tests.")
class PlatformTest(unittest.TestCase):
    def test_analyze_image_creates_history_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            platform = ImageCompressionPlatform(temp / "records.json", temp / "uploads")

            record = platform.analyze_image(ROOT / "sample_images" / "sample-gradient.png")

            self.assertEqual("sample-gradient.png", record.image_name)
            self.assertTrue(record.result_label.startswith("Rank"))
            self.assertEqual(1, len(platform.history()))
            self.assertIn("singular_values", record.features)


if __name__ == "__main__":
    unittest.main()
