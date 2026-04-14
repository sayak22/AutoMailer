import os
import time

from config import (
    SENDER_EMAIL,
    SENDER_PASSWORD,
    LOGS_FOLDER,
    PENDING_FOLDER,
    DELAY_SECONDS,
    REQUIRED_FIELDS,
    MAX_DAILY_EMAILS,
)
from logger import Logger
from csv_handler import load_csv, save_csv, list_pending_csv_paths, archive_csv, is_row_incomplete
from mailer import connect_smtp, dispatch_email


def _status(row: dict) -> str:
    return str(row.get("sent", "")).strip().lower()


def main():
    log = Logger(LOGS_FOLDER)

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        log.log("❌ SENDER_EMAIL / SENDER_PASSWORD not set. Add them as env vars or GitHub secrets.")
        log.write_footer(0, 0, 0, "N/A", "N/A")
        return

    if MAX_DAILY_EMAILS < 1:
        log.log(f"❌ MAX_DAILY_EMAILS must be >= 1 (got {MAX_DAILY_EMAILS}).")
        log.write_footer(0, 0, 0, "N/A", "N/A")
        return

    if not os.path.isdir(PENDING_FOLDER):
        log.log(f"⚠️  '{PENDING_FOLDER}/' folder not found.")
        log.write_footer(0, 0, 0, "N/A", "N/A")
        return

    initial_paths = list_pending_csv_paths()
    if not initial_paths:
        log.log(f"📭 No CSV files in '{PENDING_FOLDER}/'. Nothing to do today.")
        log.write_footer(0, 0, 0, "N/A", "N/A")
        return

    n = len(initial_paths)
    log.log(
        f"📂 Found {n} CSV file(s) in {PENDING_FOLDER}/. "
        f"Target: {MAX_DAILY_EMAILS} dispatch attempts (sent + failed) this run, across files as needed.\n"
    )

    server = connect_smtp(log)
    if not server:
        log.write_footer(0, 0, 0, "N/A", "N/A")
        return

    sent_count = error_count = skipped_count = 0
    csv_display_names: list[str] = []
    archived_basenames: list[str] = []

    while (sent_count + error_count) < MAX_DAILY_EMAILS:
        paths = list_pending_csv_paths()
        if not paths:
            break

        csv_path = paths[0]
        rows, fieldnames = load_csv(csv_path)

        pending_rows = [r for r in rows if _status(r) not in ("yes", "skipped")]
        if not pending_rows:
            log.log(f"✅ All rows already processed — {csv_path}")
            archive_csv(csv_path, log)
            bn = os.path.basename(csv_path)
            archived_basenames.append(bn)
            csv_display_names.append(bn)
            continue

        csv_display_names.append(os.path.basename(csv_path))
        log.log(f"📂 Processing : {csv_path}  (pending rows: {len(pending_rows)})")

        for row in rows:
            if _status(row) in ("yes", "skipped"):
                continue

            if (sent_count + error_count) >= MAX_DAILY_EMAILS:
                log.log(f"\n  ⏸️  Reached daily target of {MAX_DAILY_EMAILS} dispatch attempts. Stopping until next run.")
                break

            if is_row_incomplete(row):
                missing = [f for f in REQUIRED_FIELDS if not row.get(f, "").strip()]
                log.log(f"  ⏭️  SKIPPED  | Missing: {', '.join(missing)} | Row: {dict(row)}")
                row["sent"] = "skipped"
                skipped_count += 1
                save_csv(csv_path, rows, fieldnames)
                continue

            name          = row["name"].strip()
            company       = row["company"].strip()
            email         = row["mail"].strip()
            design_format = row.get("designFormat", "HR").strip()

            try:
                dispatch_email(server, email, name, company, design_format)
                row["sent"] = "yes"
                sent_count += 1
                log.log(f"  ✅ SENT     | {name} | {company} | {email}")
            except Exception as e:
                error_count += 1
                log.log(f"  ❌ FAILED   | {name} | {company} | {email} | Reason: {e}")

            save_csv(csv_path, rows, fieldnames)
            time.sleep(DELAY_SECONDS)

        unresolved = [r for r in rows if _status(r) == "no"]
        if not unresolved:
            archive_csv(csv_path, log)
            archived_basenames.append(os.path.basename(csv_path))

    server.quit()

    attempts = sent_count + error_count
    if attempts < MAX_DAILY_EMAILS and not list_pending_csv_paths():
        log.log(f"\n📭 Not enough pending rows to reach {MAX_DAILY_EMAILS} dispatch attempts this run (attempts={attempts}).")

    log.log(f"\n{'='*40}")
    log.log(f"  ✅ Sent    : {sent_count}")
    log.log(f"  ⏭️  Skipped : {skipped_count}")
    log.log(f"  ❌ Failed  : {error_count}")
    log.log(f"{'='*40}")

    csv_display = ", ".join(csv_display_names) if csv_display_names else "N/A"

    still_pending = list_pending_csv_paths()
    if still_pending:
        names = ", ".join(os.path.basename(p) for p in still_pending)
        extra = f"; archived this run: {', '.join(archived_basenames)}" if archived_basenames else ""
        archive_note = f"No — still in pending/: {names}{extra}"
    elif archived_basenames:
        archive_note = f"Yes → sent/ ({', '.join(archived_basenames)})"
    else:
        archive_note = "N/A"

    log.write_footer(sent_count, skipped_count, error_count, csv_display, archive_note)


if __name__ == "__main__":
    main()
