from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import numpy  # noqa: F401
    from PIL import Image  # noqa: F401
except ImportError:
    numpy = None


@unittest.skipIf(numpy is None, "NumPy and Pillow are required for compression tests.")
class CompressionTest(unittest.TestCase):
    def test_svd_compression_creates_rank_variants(self) -> None:
        from compression_platform.compression import compress_image

        with tempfile.TemporaryDirectory() as directory:
            result = compress_image(ROOT / "sample_images" / "sample-gradient.png", Path(directory))

            self.assertGreaterEqual(len(result.variants), 2)
            self.assertGreater(result.max_rank, 0)
            self.assertIn("SVD", result.to_dict()["method"])
            for variant in result.variants:
                self.assertTrue((Path(directory) / variant.filename).exists())
                self.assertGreaterEqual(variant.quality_score, 0)
                self.assertLessEqual(variant.quality_score, 1)


if __name__ == "__main__":
    unittest.main()
