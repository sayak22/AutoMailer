import time

from config import SENDER_EMAIL, SENDER_PASSWORD, LOGS_FOLDER, DELAY_SECONDS, REQUIRED_FIELDS, MAX_DAILY_EMAILS
from logger import Logger
from csv_handler import load_csv, save_csv, pick_pending_csv, archive_csv, is_row_incomplete
from mailer import connect_smtp, dispatch_email


def main():
    log = Logger(LOGS_FOLDER)

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        log.log("❌ SENDER_EMAIL / SENDER_PASSWORD not set. Add them as env vars or GitHub secrets.")
        log.write_footer(0, 0, 0, "N/A", archived=False)
        return

    csv_path = pick_pending_csv(log)
    if not csv_path:
        log.write_footer(0, 0, 0, "N/A", archived=False)
        return

    rows, fieldnames = load_csv(csv_path)

    pending = [r for r in rows if r.get("sent", "").strip().lower() not in ("yes", "skipped")]
    log.log(f"📋 Total rows : {len(rows)}  |  Pending : {len(pending)}\n")

    if not pending:
        log.log("✅ All rows already processed. Archiving file.")
        archive_csv(csv_path, log)
        log.write_footer(0, 0, 0, csv_path, archived=True)
        return

    server = connect_smtp(log)
    if not server:
        log.write_footer(0, 0, 0, csv_path, archived=False)
        return

    sent_count = error_count = skipped_count = 0

    for row in rows:
        if row.get("sent", "").strip().lower() in ("yes", "skipped"):
            continue

        if (sent_count + error_count) >= MAX_DAILY_EMAILS:
            log.log(f"\n  ⏸️  Reached daily limit of {MAX_DAILY_EMAILS} dispatch attempts. Pausing file until tomorrow.")
            break

        if is_row_incomplete(row):
            missing = [f for f in REQUIRED_FIELDS if not row.get(f, "").strip()]
            log.log(f"  ⏭️  SKIPPED  | Missing: {', '.join(missing)} | Row: {dict(row)}")
            row["sent"] = "skipped"
            skipped_count += 1
            save_csv(csv_path, rows, fieldnames)
            continue

        name    = row["name"].strip()
        company = row["company"].strip()
        email   = row["mail"].strip()

        try:
            dispatch_email(server, email, name, company)
            row["sent"] = "yes"
            sent_count += 1
            log.log(f"  ✅ SENT     | {name} | {company} | {email}")
        except Exception as e:
            error_count += 1
            log.log(f"  ❌ FAILED   | {name} | {company} | {email} | Reason: {e}")

        save_csv(csv_path, rows, fieldnames)
        time.sleep(DELAY_SECONDS)

    server.quit()

    log.log(f"\n{'='*40}")
    log.log(f"  ✅ Sent    : {sent_count}")
    log.log(f"  ⏭️  Skipped : {skipped_count}")
    log.log(f"  ❌ Failed  : {error_count}")
    log.log(f"{'='*40}")

    unresolved = [r for r in rows if r.get("sent", "").strip().lower() == "no"]
    archived   = not unresolved

    if unresolved:
        log.log(f"\n⚠️  {len(unresolved)} email(s) remain (failed or postponed) — file stays in pending/ for tomorrow.")
    else:
        archive_csv(csv_path, log)

    log.write_footer(sent_count, skipped_count, error_count, csv_path, archived=archived)


if __name__ == "__main__":
    main()
