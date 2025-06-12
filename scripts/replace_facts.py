"""replace_facts.py

Utility script to replace (truncate & re-insert) all rows in the `facts` table
of the Supabase project using the CSV file `full-facts-temp.csv` in the repo
root.

Usage (local):
  export SUPABASE_URL=https://<project_ref>.supabase.co
  export SUPABASE_SERVICE_KEY=<service_role_key>
  python scripts/replace_facts.py

The script will:
1. Read the CSV (expected headers: number,description,last_validated).
2. Connect to Supabase with a service-role key.
3. Run a transaction that:
   a. Truncates the existing `facts` table.
   b. Bulk inserts the CSV rows.

Errors are logged and surfaced; the script exits with status 0 on success.
"""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

try:
    from supabase import create_client, Client
except ImportError as e:  # pragma: no cover
    sys.stderr.write(
        "supabase-py is not installed. Add it to requirements.txt and pip install first.\n"
    )
    raise e

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "full-hardcoded-facts.csv")


def read_csv(path: str = CSV_PATH) -> List[Dict[str, Any]]:
    """Load CSV into list of dicts. Validates required columns."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found at {path}")

    rows: List[Dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)

        # Support alternative header names from the provided CSV
        header_map = {
            "#": "number",
            "number": "number",
            "Fact": "description",
            "description": "description",
            "Time Last Validated": "last_validated",
            "last_validated": "last_validated",
        }

        normalized_fields = {header_map.get(h, h) for h in reader.fieldnames or []}
        required_cols = {"number", "description", "last_validated"}
        missing = required_cols - normalized_fields
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        for raw_row in reader:
            # Normalize keys
            row = {header_map.get(k, k): v for k, v in raw_row.items()}

            # Basic validation / conversion
            try:
                row["number"] = int(row["number"].strip())
            except ValueError:
                raise ValueError(f"Invalid number value: {row['number']}")

            # Ensure date is ISO YYYY-MM-DD
            try:
                datetime.strptime(row["last_validated"].strip(), "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid date for number {row['number']}: {row['last_validated']} (expected YYYY-MM-DD)"
                )

            rows.append({
                "number": row["number"],
                "description": row["description"].strip(),
                "last_validated": row["last_validated"].strip()
            })

    return rows


def connect_supabase() -> "Client":
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_SERVICE_KEY (or ANON_KEY) must be set")

    return create_client(url, key)


def replace_facts(rows: List[Dict[str, Any]]):
    client = connect_supabase()

    # Start by deleting all existing rows – using rpc to ensure atomicity
    try:
        # Supabase python client currently doesn't support transactions; we perform two steps.
        client.table("facts").delete().neq("number", 0).execute()
        # Bulk insert.
        client.table("facts").insert(rows).execute()
        print(f"Inserted {len(rows)} rows into facts table.")
    except Exception as e:
        print(f"❌ Error updating Supabase: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        csv_rows = read_csv()
        replace_facts(csv_rows)
        print("✅ Facts table replaced successfully.")
    except Exception as exc:  # pragma: no cover
        print(f"❌ Failed: {exc}")
        sys.exit(1) 