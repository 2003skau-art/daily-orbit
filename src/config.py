import yaml
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
with (ROOT / "config/categories.yml").open(encoding="utf-8") as f:
    CATEGORIES = yaml.safe_load(f)["categories"]
