from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from compression_platform.web import create_app


app = create_app(project_root=ROOT)


if __name__ == "__main__":
    app.run(debug=True)
