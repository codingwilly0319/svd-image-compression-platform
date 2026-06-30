from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from compression_platform.cli import PlatformCLI


if __name__ == "__main__":
    PlatformCLI(project_root=ROOT).run()
