
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Identify the reports directory
report_dir = Path(__file__).resolve().parent / "reports"

# Retention rules (days)
retention_rules = {
    "health_*.csv": 14,
    "summary_*.csv": 30
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--apply",
    action="store_true",
    help="Actually delete expired files"
)
args = parser.parse_args()

now = datetime.now()
expired_count = 0

print("=== NETWORK REPORT CLEANUP ===")

for pattern, retention_days in retention_rules.items():

    cutoff = now - timedelta(days=retention_days)

    for file in report_dir.glob(pattern):

        modified = datetime.fromtimestamp(
            file.stat().st_mtime
        )

        if modified < cutoff:
            expired_count += 1

            if args.apply:
                file.unlink()
                print(f"[DELETED] {file.name}")
            else:
                print(f"[WOULD DELETE] {file.name}")

print(f"\nExpired reports found: {expired_count}")

if not args.apply:
    print("Dry run only. No files were deleted.")
else:
    print("Cleanup complete.")
