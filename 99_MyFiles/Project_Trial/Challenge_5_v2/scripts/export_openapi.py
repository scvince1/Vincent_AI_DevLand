"""
Export the FastAPI OpenAPI schema to contracts/api-contract.yaml.

Run from project root:
    python scripts/export_openapi.py
"""
import os
import sys

# Add project root to path so `backend` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from backend.app.main import app

schema = app.openapi()
output_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "contracts",
    "api-contract.yaml",
)

with open(output_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(schema, f, allow_unicode=True, sort_keys=False)

paths = schema.get("paths", {})
print(f"Exported {len(paths)} paths to {output_path}")
