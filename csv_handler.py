import csv
import datetime
import os
import shutil

from config import PENDING_FOLDER, SENT_FOLDER, REQUIRED_FIELDS
from logger import Logger


def is_row_incomplete(row: dict) -> bool:
    return any(not row.get(field, "").strip() for field in REQUIRED_FIELDS)


def save_csv(path: str, rows: list, fieldnames: list):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_csv(path: str) -> tuple[list, list]:
    """Returns (rows, fieldnames). Adds a 'sent' column if missing."""
    with open(path, newline="", encoding="utf-8") as f:
        reader     = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows       = list(reader)

    if "sent" not in fieldnames:
        fieldnames.append("sent")
        for row in rows:
            row.setdefault("sent", "no")

    return rows, fieldnames


def pick_pending_csv(log: Logger) -> str | None:
    if not os.path.isdir(PENDING_FOLDER):
        log.log(f"⚠️  '{PENDING_FOLDER}/' folder not found.")
        return None

    files = sorted(f for f in os.listdir(PENDING_FOLDER) if f.lower().endswith(".csv"))

    if not files:
        log.log(f"📭 No CSV files in '{PENDING_FOLDER}/'. Nothing to do today.")
        return None

    chosen = os.path.join(PENDING_FOLDER, files[0])
    log.log(f"📂 Selected file : {chosen}")
    if len(files) > 1:
        log.log(f"   ({len(files) - 1} more file(s) queued for future days)")
    return chosen


def archive_csv(csv_path: str, log: Logger):
    os.makedirs(SENT_FOLDER, exist_ok=True)
    filename = os.path.basename(csv_path)
    dest     = os.path.join(SENT_FOLDER, filename)

    if os.path.exists(dest):
        base, ext = os.path.splitext(filename)
        stamp     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest      = os.path.join(SENT_FOLDER, f"{base}_{stamp}{ext}")

    shutil.move(csv_path, dest)
    log.log(f"📁 Archived '{csv_path}' → '{dest}'")
