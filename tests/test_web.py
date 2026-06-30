from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import flask  # noqa: F401
except ImportError:
    flask = None


@unittest.skipIf(flask is None, "Flask is not installed.")
class WebRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        from compression_platform.web import create_app

        self.app = create_app(project_root=ROOT)
        self.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = self.app.test_client()

    def test_login_page_loads(self) -> None:
        response = self.client.get("/login")

        self.assertEqual(200, response.status_code)
        self.assertIn("SVD 圖像壓縮平台".encode("utf-8"), response.data)

    def test_operator_login_opens_dashboard(self) -> None:
        response = self.client.post(
            "/login",
            data={"username": "operator", "password": "operator123"},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn("SVD 圖像壓縮總覽".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
