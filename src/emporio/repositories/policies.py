
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[3]
POLICIES_PATH = ROOT / "config" / "policies.yaml"

with open(POLICIES_PATH, encoding="utf-8") as file:
    policies = yaml.safe_load(file)


def get_policy(topic: str) -> dict | None:
    return policies.get(topic)